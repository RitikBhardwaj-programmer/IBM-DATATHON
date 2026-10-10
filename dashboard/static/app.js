/* Zero Exposure dashboard. Plain JS + Chart.js (vendored). All numbers come from the API; nothing here is a result.
   Sections: helpers/theme -> run state + event handler -> live/replay controllers -> panel 1 charts -> panel 2 -> panel 3. */
'use strict';

// ============================================================ helpers + theme
const $ = (id) => document.getElementById(id);
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const MARKERS = ['circle', 'rect', 'triangle', 'rectRot'];            // one marker shape per hospital, so colour is never the only cue
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const nf = new Intl.NumberFormat('en-US');
const fmtBytes = (b) => (b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(1)} KB` : `${(b / 1048576).toFixed(2)} MB`);
const saveLS = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode: fine */ } };
const loadLS = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };

const FONT = '"IBM Plex Sans", system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';   // vendored in static/vendor/fonts; same stack as styles.css
function C() {
  return { text: css('--text'), muted: css('--muted'), grid: css('--grid'), accent: css('--model'), lock: css('--lock'), lockFill: css('--lock-fill'), sky: css('--sky'),
    good: css('--good'), warn: css('--warn'), bad: css('--bad'), panel: css('--surface'),
    hosp: [0, 1, 2, 3].map((i) => css('--h' + i)), fedavg: css('--fedavg'), fedprox: css('--fedprox') };
}

const registry = [];                                   // [{chart, style}] so a theme switch can recolour every chart
function register(chart, style) { registry.push({ chart, style }); restyleOne({ chart, style }); return chart; }
function unregister(chart) { const i = registry.findIndex((r) => r.chart === chart); if (i >= 0) registry.splice(i, 1); chart.destroy(); }
function restyleOne({ chart, style }) {
  const c = C();
  for (const s of Object.values(chart.options.scales || {})) {
    if (!s.ticks) s.ticks = {}; s.ticks.color = c.muted;     // never `s.x = s.x || {}`: assigning an options proxy to itself recurses forever
    if (!s.grid) s.grid = {}; s.grid.color = c.grid;
    if (!s.border) s.border = {}; s.border.color = c.grid;
    if (s.title) s.title.color = c.muted;
  }
  if (chart.options.plugins.legend && chart.options.plugins.legend.labels) chart.options.plugins.legend.labels.color = c.text;
  style(chart, c);
  chart.update('none');
}
function restyleAll() {
  Chart.defaults.color = css('--muted');
  registry.forEach(restyleOne);
  drawHero();
}

Chart.defaults.font.size = 15;
Chart.defaults.font.family = FONT;
Chart.defaults.animation = false;   // colours are set right after construction; an animated first draw then fails (_fn is not a function). Updates are instant anyway
Chart.defaults.plugins.tooltip.titleFont = { size: 15 };
Chart.defaults.plugins.tooltip.bodyFont = { size: 14 };

function baseOptions(extra = {}) {
  return Object.assign({ responsive: true, maintainAspectRatio: false, interaction: { mode: 'nearest', intersect: false },
    plugins: { legend: { display: false } } }, extra);
}
const axisTitle = (text) => ({ display: true, text, font: { size: 14, weight: '600' } });

// theme toggle: explicit choice wins, else the OS setting
function effectiveTheme() { return document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'); }
function syncThemeBtn() { $('themeBtn').textContent = effectiveTheme() === 'dark' ? 'Light theme' : 'Dark theme'; }
function setTheme(t) { document.documentElement.dataset.theme = t; saveLS('theme', t); syncThemeBtn(); requestAnimationFrame(restyleAll); }
{ const saved = loadLS('theme'); if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved; }
$('themeBtn').addEventListener('click', () => setTheme(effectiveTheme() === 'dark' ? 'light' : 'dark'));
matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => { syncThemeBtn(); requestAnimationFrame(restyleAll); });
syncThemeBtn();

async function getJSON(url, opts) {
  const r = await fetch(url, opts);
  let body = null;
  try { body = await r.json(); } catch (e) { /* not JSON */ }
  if (!r.ok) { const err = new Error((body && body.detail && JSON.stringify(body.detail)) || r.statusText); err.status = r.status; err.body = body; throw err; }
  return body;
}

// ============================================================ run state
const STAGE_IDX = { setup: 0, share_keys: 1, collect_masked_vectors: 2, unmask: 3 };
const STAGE_NAME = ['setup', 'share keys', 'masked upload', 'unmask'];
const S = {};
let pendingStop = false, mode = 'live', es = null, replayTimer = null, token = 0, startTimer = null, startedAt = 0, renderQueued = false;

let DEFAULT_NAMES = ['hospital 1', 'hospital 2', 'hospital 3', 'hospital 4'];   // replaced by the real names (from the recorded run) at boot
function resetState() {
  Object.assign(S, { phase: 'idle', base: null, hospitals: DEFAULT_NAMES.slice(), rounds: [], nRounds: 0, seen: new Set(), majority: null,
    plainMode: false, up: 0, down: 0, runId: null, lastStage: null, cells: {}, curRound: {} });
}
resetState();

const TERMINAL = new Set(['done', 'stopped', 'error']);
function handle(ev) {
  switch (ev.type) {
    case 'run': S.runId = ev.id || S.runId; if (ev.params) reflectParams(ev.params); if (S.phase === 'idle') setPhase('starting'); break;
    case 'meta': if (ev.params) reflectParams(ev.params); break;
    case 'baseline':
      if (S.base) break;   // an SSE reconnect replays the run from the start: every event is applied once only (see also S.seen in onStage)
      S.base = ev; S.hospitals = ev.hospitals; S.nRounds = ev.rounds; S.plainMode = !ev.secagg;
      loadMajority(ev.seed); refreshInspectLabel();
      buildHospitalCharts(); buildStrip(); setPhase(S.phase === 'preview' ? 'preview' : (mode === 'replay' ? 'replay' : 'running')); break;
    case 'round': S.rounds[ev.round] = ev; if (!S.nRounds) S.nRounds = ev.total_rounds;
      $('srv').textContent = `Round ${ev.round} of ${ev.total_rounds}. Global accuracy ${pct(ev.acc)}.`; break;
    case 'stage': onStage(ev); break;
    case 'inspect_ready': if (S.phase !== 'preview') loadInspect(ev.id, 'live run ' + ev.id); break;
    case 'done': finish('done'); break;
    case 'stopped': finish('stopped'); break;
    case 'run_error': finish('error', ev); break;
    default: break;
  }
  scheduleRender();
}

function onStage(ev) {
  const key = `${ev.hospital}|${ev.round}|${ev.stage}`;
  if (S.seen.has(key)) return;   // replayed after a reconnect: do not count its bytes twice
  S.seen.add(key);
  S.up += ev.bytes_out || 0; S.down += ev.bytes_in || 0; S.lastStage = ev;
  const cell = S.cells[ev.hospital] && S.cells[ev.hospital][ev.round];
  if (!cell) return;
  const idx = S.plainMode || ev.stage === 'plain_fit' ? 0 : STAGE_IDX[ev.stage];
  if (idx === undefined) return;
  const b = cell.children[idx];
  b.classList.add('on'); if (S.plainMode || ev.stage === 'plain_fit') b.classList.add('plainx');
  if (!REDUCED) { b.classList.remove('flash'); void b.offsetWidth; b.classList.add('flash'); }
  const prev = S.curRound[ev.hospital]; if (prev && prev !== cell) prev.classList.remove('cur');
  cell.classList.add('cur'); S.curRound[ev.hospital] = cell;
}

function finish(kind, ev) {
  if (es) { es.close(); es = null; }
  stopTimers();
  setPhase(kind, ev);
  document.querySelectorAll('.cell.cur').forEach((c) => c.classList.remove('cur'));
}

// ============================================================ status / banner / buttons
function setPhase(p, ev) {
  S.phase = p;
  const pill = $('statusPill'), ban = $('banner');
  const labels = { idle: 'Idle', starting: 'Starting…', running: 'Running', replay: 'Replaying', preview: 'Recorded run', done: 'Finished', stopped: 'Stopped', error: 'Failed' };
  pill.textContent = labels[p] || p; pill.className = 'pill ' + (p === 'replay' ? 'running' : p === 'preview' ? '' : p);
  const busy = p === 'starting' || p === 'running' || p === 'replay';
  $('startBtn').disabled = busy; $('stopBtn').disabled = !busy;
  $('startBtn').textContent = mode === 'live' ? 'Start live run' : 'Play replay';
  $('ctl').querySelectorAll('#liveCtl input, #replayCtl input, #replayCtl select, #modeSeg input').forEach((el) => { el.disabled = busy; });
  ban.hidden = false; ban.className = 'banner';
  if (p === 'starting') {
    ban.classList.add('info');
    startedAt = Date.now(); clearInterval(startTimer);
    const tick = () => { ban.innerHTML = `<span class="spin"></span><b>Starting Ray (~30 s)…</b> Ray is the engine that runs the four hospitals as parallel workers. It also trains the two baselines (centralized, and each hospital alone) before round 1. Elapsed: ${Math.round((Date.now() - startedAt) / 1000)} s.`; };
    tick(); startTimer = setInterval(tick, 1000);
  } else {
    clearInterval(startTimer);
  }
  if (p === 'preview') { ban.classList.add('info'); ban.innerHTML = '<b>Showing a recorded run</b> (the golden run), so every panel has real data. ' + (mode === 'live' ? '<b>Start live run</b> trains for real.' : '<b>Play replay</b> shows it round by round.'); }
  else if (p === 'running' || p === 'replay' || p === 'idle') ban.hidden = true;
  else if (p === 'done') {
    const last = S.rounds[S.rounds.length - 1];
    ban.classList.add('ok');
    ban.innerHTML = `<b>${mode === 'replay' ? 'Replay finished.' : 'Run finished.'}</b>` + (last ? ` Final global accuracy ${pct(last.acc)} after ${last.round} rounds.` : '');
  } else if (p === 'stopped') { ban.classList.add('warn'); ban.innerHTML = '<b>Run stopped.</b> The partial results are kept on screen.'; }
  else if (p === 'error') {
    ban.classList.add('err');
    const tail = ev && ev.stderr_tail ? `<pre>${esc(ev.stderr_tail)}</pre>` : '';
    ban.innerHTML = `<b>The run failed</b> (exit code ${ev && ev.exit_code !== undefined && ev.exit_code !== null ? esc(ev.exit_code) : 'unknown'}). ${tail}`;
  }
}
function note(kind, html) { const ban = $('banner'); ban.hidden = false; ban.className = 'banner ' + kind; ban.innerHTML = html; }

function stopTimers() { clearTimeout(replayTimer); replayTimer = null; clearInterval(startTimer); }
function closeStreams() { if (es) { es.close(); es = null; } stopTimers(); token++; }

function reflectParams(p) {
  if (!p) return;
  if (p.noise !== undefined) { $('noise').value = p.noise; $('noiseOut').textContent = Number(p.noise).toFixed(1); }
  if (p.strategy) document.querySelector(`input[name=strategy][value=${p.strategy}]`).checked = true;
  if (p.secagg !== undefined) { $('secagg').checked = !!p.secagg; $('secaggOut').textContent = p.secagg ? 'On' : 'Off'; }
  if (p.rounds) $('rounds').value = p.rounds;
  if (p.seed !== undefined) $('seed').value = p.seed;
  if (p.noise !== undefined && p.strategy) $('kSrc').textContent = `One run (DP noise ${Number(p.noise).toFixed(1)}, ${p.strategy === 'fedprox' ? 'FedProx' : 'FedAvg'}, SecAgg ${p.secagg ? 'on' : 'off'}, seed ${p.seed}), not the 5-seed mean above.`;
}

// ============================================================ controls
$('noise').addEventListener('input', () => { $('noiseOut').textContent = Number($('noise').value).toFixed(1); });
$('secagg').addEventListener('change', () => { $('secaggOut').textContent = $('secagg').checked ? 'On' : 'Off'; });
document.querySelectorAll('input[name=mode]').forEach((r) => r.addEventListener('change', () => {
  mode = document.querySelector('input[name=mode]:checked').value;
  $('liveCtl').hidden = mode !== 'live'; $('replayCtl').hidden = mode !== 'replay';
  $('startBtn').textContent = mode === 'live' ? 'Start live run' : 'Play replay';
  if (S.phase === 'preview') setPhase('preview');
}));

$('ctl').addEventListener('submit', (e) => { e.preventDefault(); if (mode === 'live') startLive(); else startReplay(); });
$('stopBtn').addEventListener('click', stopRun);

async function startLive() {
  const body = { noise: Math.min(5, Math.max(0, Number($('noise').value))), strategy: document.querySelector('input[name=strategy]:checked').value,
    secagg: $('secagg').checked, rounds: Math.min(30, Math.max(1, parseInt($('rounds').value, 10) || 15)),
    seed: Math.min(99, Math.max(0, parseInt($('seed').value, 10) || 0)) };
  $('rounds').value = body.rounds; $('seed').value = body.seed;
  closeStreams(); resetState(); clearPanel1(); clearInspect(); setPhase('starting');
  const my = token; pendingStop = false;
  try {
    const run = await getJSON('/api/runs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (my !== token) return;
    S.runId = run.id; attach(run.id);
    if (pendingStop) { pendingStop = false; stopRun(); }   // Stop was clicked while the POST was still in flight
  } catch (err) {
    if (my !== token) return;
    if (err.status === 409) { await attachCurrent('A run was already active (started elsewhere), so this page is now showing it.'); return; }
    setPhase('idle'); note('err', `<b>Could not start the run.</b> ${esc(err.message)}`);
    $('startBtn').disabled = false; $('stopBtn').disabled = true;
  }
}

async function attachCurrent(msg) {
  const cur = await getJSON('/api/runs/current');
  if (cur.status === 'running') {
    closeStreams(); resetState(); clearPanel1(); clearInspect(); mode = 'live';
    document.querySelector('input[name=mode][value=live]').checked = true; $('liveCtl').hidden = false; $('replayCtl').hidden = true;
    reflectParams(cur.params); setPhase('starting'); S.runId = cur.id; attach(cur.id);
    if (msg) setTimeout(() => { if (S.phase === 'starting') note('info', `<span class="spin"></span>${esc(msg)}`); }, 0);
    return true;
  }
  return false;
}

function attach(runId) {
  const my = token;
  es = new EventSource(`/api/runs/${runId}/events`);
  for (const name of ['run', 'baseline', 'round', 'stage', 'inspect_ready', 'done', 'stopped', 'run_error']) {
    es.addEventListener(name, (m) => {
      if (my !== token) return;
      let obj; try { obj = JSON.parse(m.data); } catch (e) { return; }
      if (!obj.type) obj.type = name;
      handle(obj);
    });
  }
  es.onerror = () => {
    if (my !== token || !es) return;
    if (TERMINAL.has(S.phase)) { es.close(); es = null; return; }
    if (es.readyState === EventSource.CLOSED) { es = null; finish('error', { exit_code: null, stderr_tail: 'The connection to the server was lost.' }); }
    // otherwise EventSource reconnects by itself and the server replays the run from the start
  };
}

async function stopRun() {
  if (mode === 'replay' || S.phase === 'replay') { closeStreams(); setPhase('stopped'); return; }
  $('stopBtn').disabled = true;
  if (!S.runId) { pendingStop = true; note('warn', '<span class="spin"></span>Stopping as soon as the server has created the run …'); return; }
  try { await getJSON(`/api/runs/${S.runId}/stop`, { method: 'POST' }); } catch (err) { note('err', `<b>Stop failed.</b> ${esc(err.message)}`); }
}

async function startReplay() {
  const name = $('replaySel').value;
  if (!name) { note('warn', 'No recording is available.'); return; }
  closeStreams(); resetState(); clearPanel1(); clearInspect();
  const my = token, speed = Number(document.querySelector('input[name=speed]:checked').value);
  let events;
  try { events = (await getJSON(`/api/replays/${encodeURIComponent(name)}`)).events; if (my !== token) return; } catch (err) { note('err', `<b>Could not load the recording.</b> ${esc(err.message)}`); return; }
  setPhase('replay'); loadInspect(name, `recording ${name}`);
  let i = 0;
  const step = () => {
    if (my !== token) return;
    const ev = events[i++]; handle(ev);
    if (i >= events.length) { if (!TERMINAL.has(S.phase)) finish('done'); return; }
    if (TERMINAL.has(S.phase)) return;
    const gap = Math.min(Math.max((events[i].t || 0) - (ev.t || 0), 0), 2.0) / speed;   // long start-up pauses are capped at 2 s
    replayTimer = setTimeout(step, gap * 1000);
  };
  step();
}

// instant, untimed version of the same events: the page opens already populated
async function showPreview() {
  try {
    const events = (await getJSON('/api/replays/golden_run')).events;
    resetState(); clearPanel1(); S.phase = 'preview';
    for (const ev of events) if (ev.type !== 'done') handle(ev);
    setPhase('preview');
  } catch (err) { setPhase('idle'); }
}

// ============================================================ panel 1: charts
let accChart = null, epsChart = null, hospCharts = [];

const bandsPlugin = {
  id: 'bands',
  beforeDatasetsDraw(chart) {
    const { ctx, chartArea: a, scales: { y } } = chart; if (!y || !a) return;
    const c = C(); const lo = y.min, hi = y.max;
    const band = (from, to, col, label) => {
      const f = Math.max(from, lo), t = Math.min(to, hi); if (t <= f) return;
      const y1 = y.getPixelForValue(t), y2 = y.getPixelForValue(f);
      ctx.save(); ctx.fillStyle = col; ctx.fillRect(a.left, y1, a.right - a.left, y2 - y1);
      ctx.fillStyle = c.text; ctx.globalAlpha = 0.85; ctx.font = `600 14px ${FONT}`; ctx.textBaseline = 'top'; ctx.textAlign = 'right';
      ctx.fillText(label, a.right - 8, y1 + 4); ctx.restore();
    };
    const alpha = (name, al) => { const h = c[name].replace('#', ''); const n = parseInt(h, 16); return `rgba(${n >> 16}, ${(n >> 8) & 255}, ${n & 255}, ${al / 100})`; };
    band(0, 1, alpha('good', 22), 'strong privacy: ε < 1');
    band(1, 10, alpha('warn', 20), 'moderate: 1 to 10');
    band(10, 1e9, alpha('bad', 18), 'weak: ε > 10');
  },
};
const endLabelPlugin = {
  id: 'endLabel',
  afterDatasetsDraw(chart) {
    chart.data.datasets.forEach((d, i) => {
      if (!d.endLabel || !chart.isDatasetVisible(i) || !d.data.length) return;
      const meta = chart.getDatasetMeta(i), pt = meta.data[meta.data.length - 1]; if (!pt) return;
      const { ctx, chartArea: a } = chart; ctx.save();
      ctx.fillStyle = d.borderColor; ctx.font = `700 14px ${FONT}`; ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
      ctx.fillText(d.endLabel, a.right - 6, pt.y - 6); ctx.restore();
    });
  },
};

function makeAccChart() {
  accChart = register(new Chart($('accChart'), {
    type: 'line',
    data: { datasets: [
      { label: 'Global model (federated)', data: [], pointStyle: 'circle', pointRadius: 4, borderWidth: 3, tension: 0.15 },
      { label: 'Centralized, same training budget', data: [], borderDash: [8, 6], borderWidth: 3, pointRadius: 0, endLabel: 'centralized, same training budget' },
    ] },
    options: baseOptions({
      scales: {
        x: { type: 'linear', min: 0, max: 15, title: axisTitle('Round (0 = untrained model)'), ticks: { maxTicksLimit: 16, stepSize: 1, font: { size: 14 } } },
        y: { min: 0, max: 1, title: axisTitle('Accuracy on held-out patients'), ticks: { callback: (v) => pct(v, 0), font: { size: 14 } } },
      },
      plugins: { legend: { display: true, position: 'top', labels: { usePointStyle: true, font: { size: 15 }, boxWidth: 10, boxHeight: 10, padding: 14 } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${pct(c.parsed.y, 2)}` } } },
    }),
    plugins: [endLabelPlugin],
  }), (ch, c) => { ch.data.datasets[0].borderColor = c.accent; ch.data.datasets[0].backgroundColor = c.accent; ch.data.datasets[0].pointBackgroundColor = c.accent;
    ch.data.datasets[1].borderColor = c.text; ch.data.datasets[1].backgroundColor = c.text; });
}

function makeEpsChart() {
  epsChart = register(new Chart($('epsChart'), {
    type: 'line',
    data: { datasets: [0, 1, 2, 3].map((i) => ({ label: `hospital ${i}`, data: [], pointStyle: MARKERS[i], pointRadius: 5, borderWidth: 3 })) },
    options: baseOptions({
      scales: {
        x: { type: 'linear', min: 0, max: 15, title: axisTitle('Round'), ticks: { maxTicksLimit: 16, stepSize: 1, font: { size: 14 } } },
        y: { type: 'logarithmic', min: 1, max: 100, title: axisTitle('ε so far (log scale)'),
          afterBuildTicks: (ax) => { ax.ticks = [0.1, 1, 10, 100, 1000].filter((v) => v >= ax.min && v <= ax.max).map((value) => ({ value })); },
          ticks: { callback: (v) => String(v), font: { size: 14 } } },
      },
      plugins: { legend: { display: true, position: 'top', labels: { usePointStyle: true, font: { size: 15 }, boxWidth: 10, boxHeight: 10, padding: 14 } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ε = ${c.parsed.y.toFixed(2)}` } } },
    }),
    plugins: [bandsPlugin],
  }), (ch, c) => c.hosp.forEach((col, i) => { const d = ch.data.datasets[i]; d.borderColor = col; d.backgroundColor = col; d.pointBackgroundColor = col; }));
}

function buildHospitalCharts() {
  hospCharts.forEach(unregister); hospCharts = [];
  const grid = $('hospGrid'); grid.innerHTML = '';
  S.hospitals.forEach((name, i) => {
    const card = document.createElement('div'); card.className = 'hosp-card';
    card.innerHTML = `<h4><i class="swatch ${MARKERS[i]}" style="background:var(--h${i})"></i>${esc(name)}</h4><div class="hs" id="hs${i}">&nbsp;</div><div class="chart-box mini"><canvas id="hc${i}" role="img" aria-label="Accuracy of ${esc(name)}"></canvas></div>`;
    grid.appendChild(card);
    const base = S.base ? S.base.local_per_hospital_acc[i] : null;
    const ch = new Chart($('hc' + i), {
      type: 'line',
      data: { datasets: [
        { label: 'shared model', data: [], pointStyle: MARKERS[i], pointRadius: 3, borderWidth: 3, tension: 0.15 },
        { label: 'trained alone', data: base === null ? [] : [{ x: 0, y: base }, { x: Math.max(S.nRounds, 1), y: base }], borderDash: [6, 5], borderWidth: 2, pointRadius: 0 },
        { label: 'always guess the common answer', data: [], borderDash: [2, 4], borderWidth: 2, pointRadius: 0 },
      ] },
      options: baseOptions({
        scales: { x: { type: 'linear', min: 0, max: Math.max(S.nRounds, 1), ticks: { maxTicksLimit: 6, font: { size: 13 } } },
          y: { min: 0, max: 1, ticks: { callback: (v) => pct(v, 0), stepSize: 0.25, font: { size: 13 } } } },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${pct(c.parsed.y, 1)}` } } },
      }),
    });
    hospCharts.push(register(ch, (chh, c) => { chh.data.datasets[0].borderColor = c.hosp[i]; chh.data.datasets[0].backgroundColor = c.hosp[i];
      chh.data.datasets[0].pointBackgroundColor = c.hosp[i]; chh.data.datasets[1].borderColor = c.muted; chh.data.datasets[2].borderColor = c.text; }));
  });
}

function buildStrip() {
  const strip = $('strip'); strip.innerHTML = ''; S.cells = {}; S.curRound = {};
  const N = S.nRounds;
  S.hospitals.forEach((name, h) => {
    const row = document.createElement('div'); row.className = 'srow';
    row.innerHTML = `<div class="sl"><i class="swatch ${MARKERS[h]}" style="background:var(--h${h})"></i><span>${esc(name)}</span></div>`;
    const cells = document.createElement('div'); cells.className = 'cells'; S.cells[h] = {};
    for (let r = 1; r <= N; r++) {
      const c = document.createElement('div'); c.className = 'cell' + (S.plainMode ? ' plain-mode' : ''); c.title = `${name}, round ${r}`;
      c.innerHTML = S.plainMode ? '<i></i>' : '<i></i><i></i><i></i><i></i>';
      cells.appendChild(c); S.cells[h][r] = c;
    }
    row.appendChild(cells); strip.appendChild(row);
  });
  const nums = document.createElement('div'); nums.className = 'rnums';
  nums.innerHTML = '<span>round</span>';
  const nc = document.createElement('div'); nc.className = 'cells';
  for (let r = 1; r <= N; r++) nc.innerHTML += `<span>${r === 1 || r % 5 === 0 || r === N ? r : ''}</span>`;
  nums.appendChild(nc); strip.appendChild(nums);
  $('stripNow').textContent = S.plainMode ? 'SecAgg+ is off in this run: each hospital sends its plain weights in one step (red blocks).' : '';
}

function clearPanel1() {
  S.cells = {}; $('strip').innerHTML = ''; $('stripNow').textContent = ''; $('hospGrid').innerHTML = '';
  hospCharts.forEach(unregister); hospCharts = [];
  ['kRound', 'kAcc', 'kCen', 'kEps', 'kBytes'].forEach((k) => { $(k).textContent = '–'; }); $('kBytesSub').textContent = ''; $('prog').value = 0;
  $('epsNote').hidden = true;
  for (const ch of [accChart, epsChart]) if (ch) { ch.data.datasets.forEach((d) => { d.data = []; }); ch.update('none'); }
}

function scheduleRender() { if (!renderQueued) { renderQueued = true; requestAnimationFrame(() => { renderQueued = false; render(); }); } }

function render() {
  const N = S.nRounds || 15, rs = S.rounds.filter(Boolean), last = rs[rs.length - 1], base = S.base;
  // KPIs
  $('kRound').textContent = last ? `${last.round} / ${last.total_rounds}` : '–';
  $('kAcc').textContent = last ? pct(last.acc) : '–';
  $('prog').value = last && last.total_rounds ? Math.round(last.round / last.total_rounds * 100) : 0;
  $('kCen').textContent = base ? pct(base.central_acc) : '–';
  const eps = last && last.epsilon ? last.epsilon.filter((v) => v !== null) : [];
  $('kEps').textContent = !last ? '–' : eps.length ? Math.max(...eps).toFixed(1) : '∞ (no DP)';
  $('kBytes').textContent = S.up + S.down ? fmtBytes(S.up + S.down) : '–';
  $('kBytesSub').textContent = S.up + S.down ? `↑ ${fmtBytes(S.up)} to server · ↓ ${fmtBytes(S.down)} back` : '';
  // accuracy chart
  if (accChart) {
    const acc = rs.map((r) => ({ x: r.round, y: r.acc }));
    const ys = acc.map((p) => p.y).concat(base ? [base.central_acc] : []);
    const lo = ys.length ? Math.max(0, Math.floor((Math.min(...ys) - 0.03) * 10) / 10) : 0, hi = ys.length ? Math.min(1, Math.ceil((Math.max(...ys) + 0.03) * 10) / 10) : 1;
    accChart.options.scales.x.max = N; accChart.options.scales.y.min = lo; accChart.options.scales.y.max = hi;
    accChart.data.datasets[0].data = acc;
    accChart.data.datasets[1].data = base ? [{ x: 0, y: base.central_acc }, { x: N, y: base.central_acc }] : [];
    accChart.update('none');
  }
  // epsilon chart
  if (epsChart) {
    const hasEps = rs.some((r) => r.epsilon && r.epsilon.some((v) => v !== null));
    const dp = base && base.noise > 0;
    let vmin = Infinity, vmax = 0;
    [0, 1, 2, 3].forEach((h) => {
      const pts = rs.filter((r) => r.round >= 1 && r.epsilon && r.epsilon[h] !== null && r.epsilon[h] > 0).map((r) => ({ x: r.round, y: r.epsilon[h] }));
      pts.forEach((p) => { vmin = Math.min(vmin, p.y); vmax = Math.max(vmax, p.y); });
      epsChart.data.datasets[h].data = pts; epsChart.data.datasets[h].label = S.hospitals[h];
    });
    epsChart.options.scales.x.max = N;
    if (vmax > 0) { epsChart.options.scales.y.min = vmin < 1 ? Math.pow(10, Math.floor(Math.log10(vmin))) : 1; epsChart.options.scales.y.max = Math.pow(10, Math.ceil(Math.log10(vmax * 1.05))); }
    else { epsChart.options.scales.y.min = 1; epsChart.options.scales.y.max = 100; }
    const nt = $('epsNote');
    if (base && !dp) { nt.hidden = false; nt.innerHTML = '<b>Noise is 0, so there is no differential privacy.</b> ε is unbounded (∞) and there is nothing to plot. Masking (SecAgg+) still hides single updates from the server.'; }
    else if (rs.length && !hasEps && base) { nt.hidden = false; nt.textContent = 'No ε reported for this run.'; } else nt.hidden = true;
    epsChart.update('none');
  }
  // hospital small multiples
  hospCharts.forEach((ch, h) => {
    ch.options.scales.x.max = Math.max(N, 1);
    ch.data.datasets[0].data = rs.map((r) => ({ x: r.round, y: r.per_hospital_acc[h] }));
    if (base) ch.data.datasets[1].data = [{ x: 0, y: base.local_per_hospital_acc[h] }, { x: Math.max(N, 1), y: base.local_per_hospital_acc[h] }];
    const mj = S.majority && S.majority[S.hospitals[h]] ? S.majority[S.hospitals[h]].majority_acc : null;
    ch.data.datasets[2].data = mj === null ? [] : [{ x: 0, y: mj }, { x: Math.max(N, 1), y: mj }];
    ch.update('none');
    const el = $('hs' + h);
    if (el && base) el.textContent = (last ? `alone ${pct(base.local_per_hospital_acc[h])} → shared ${pct(last.per_hospital_acc[h])}` : `alone ${pct(base.local_per_hospital_acc[h])}`)
      + (mj === null ? '' : ` · guess-common ${pct(mj)}`);
  });
  renderMajorityNote();
  // strip status line
  const ls = S.lastStage;
  if (ls && !S.plainMode) {
    const idx = STAGE_IDX[ls.stage];
    $('stripNow').textContent = `Latest: ${S.hospitals[ls.hospital]}, round ${ls.round}, step ${idx + 1} of 4 (${STAGE_NAME[idx]}).`;
  }
}

// majority-class reference: accuracy of always answering the more common label of the hospital's own test set (computed by the server from the data)
const majorityCache = new Map();
async function loadMajority(seed) {
  if (seed === undefined || seed === null) return;
  const my = token;
  try {
    if (!majorityCache.has(seed)) majorityCache.set(seed, (await getJSON(`/api/majority/${encodeURIComponent(seed)}`)).hospitals);
    if (my !== token) return;
    S.majority = majorityCache.get(seed); scheduleRender();
  } catch (err) { /* data files missing on this machine: the reference is simply not shown */ }
}
function renderMajorityNote() {
  const el = $('majNote'); if (!S.majority) { el.textContent = ''; return; }
  const alone = S.base ? S.base.local_per_hospital_acc : [];
  let t = "Dotted line = the score of always answering the more common label of that hospital's own test patients (no model at all).";
  S.hospitals.forEach((n, h) => {
    const m = S.majority[n];
    if (!m || alone[h] === undefined || alone[h] > m.majority_acc + 0.015) return;   // only where "alone" is no better than guessing
    const label = m.disease_rate >= 0.5 ? 'disease' : 'no disease';
    t += ` ${n}: ${pct(m.disease_rate, 0)} of its ${m.n_test} test patients have heart disease, so always answering "${label}" scores ${pct(m.majority_acc, 0)}, and its "alone" model (${pct(alone[h])}) does no better: that high number is not evidence of a good model.`;
  });
  el.textContent = t;
}

// ============================================================ panel 2: what the server sees
let plainQChart = null, maskedChart = null, rawChart = null, aggChart = null;
let inspectSeq = 0, lastInspect = null;      // inspectSeq: only the newest load may draw (a late golden-preview response must not overwrite a live run)

function clearInspect() {
  inspectSeq++; lastInspect = null;
  for (const ch of [plainQChart, maskedChart, rawChart, aggChart]) if (ch) { ch.data.datasets[0].data = []; ch.update('none'); }
  $('seesSource').textContent = 'Waiting for the capture of round 1 …'; $('badge').className = 'badge'; $('badge').textContent = ''; $('seesStats').textContent = '';
  renderHeroStrip(null);
}
function seesSourceHtml() {
  if (!lastInspect) return '';
  const info = lastInspect.d.info, hosp = S.hospitals[info.hospital] || `hospital #${Number(info.hospital) + 1}`;
  return `Source: <b>${esc(lastInspect.label)}</b> · hospital <b>${esc(hosp)}</b> · round <b>${Number(info.round)}</b> · captured at step <b>${esc(String(info.stage).replace(/_/g, ' '))}</b>`;
}
function refreshInspectLabel() { if (lastInspect) $('seesSource').innerHTML = seesSourceHtml(); }   // the hospital names arrive with the baseline event

const needlePlugin = { id: 'expected', afterDatasetsDraw(chart, _a, opts) {
  if (!opts || !opts.value) return;
  const { ctx, chartArea: a, scales: { y } } = chart, py = y.getPixelForValue(opts.value);
  ctx.save(); ctx.strokeStyle = opts.color; ctx.setLineDash([8, 6]); ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(a.left, py); ctx.lineTo(a.right, py); ctx.stroke();
  ctx.setLineDash([]); ctx.fillStyle = opts.color; ctx.font = `600 13px ${FONT}`; ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
  ctx.fillText(opts.label, a.right - 6, py - 4); ctx.restore();
} };

function sharedAxisChart(canvas, showTicks, ytitle) {
  return new Chart(canvas, {
    type: 'bar', data: { datasets: [{ data: [], borderWidth: 1 }] },
    options: baseOptions({
      interaction: { mode: 'nearest', intersect: true },
      layout: { padding: { right: 14 } },
      scales: {
        x: { type: 'linear', offset: false, min: 0, max: 4294967296, title: showTicks ? axisTitle('Value on the number line 0 … 2³² (modular range, 4,294,967,296)') : { display: false },
          ticks: { display: showTicks, stepSize: 1073741824, font: { size: 14 },
            callback: (v) => ({ 0: '0', 1073741824: '¼', 2147483648: '½', 3221225472: '¾', 4294967296: '2³²' }[v] ?? '') } },
        y: { beginAtZero: true, title: axisTitle(ytitle), afterFit: (s) => { s.width = 64; }, ticks: { font: { size: 13 }, precision: 0 } },
      },
      plugins: { legend: { display: false }, expected: {} },
    }),
    plugins: [needlePlugin],
  });
}

function histValues(vals, lo, hi, bins) {
  const counts = new Array(bins).fill(0), w = (hi - lo) / bins;
  vals.forEach((v) => { let b = Math.floor((v - lo) / w); if (b >= bins) b = bins - 1; if (b < 0) b = 0; counts[b]++; });
  return { counts, w, centers: counts.map((_, i) => lo + (i + 0.5) * w) };
}

function makeInspectCharts() {
  plainQChart = register(sharedAxisChart($('plainQChart'), false, 'values'), (ch, c) => { const d = ch.data.datasets[0]; d.backgroundColor = c.bad; d.borderColor = c.bad; });
  maskedChart = register(sharedAxisChart($('maskedChart'), true, 'values per bin'), (ch, c) => {
    const d = ch.data.datasets[0]; d.backgroundColor = c.lock; d.borderColor = c.panel; ch.options.plugins.expected.color = c.text; });
  const hist = (canvas, xt) => new Chart(canvas, {
    type: 'bar', data: { datasets: [{ data: [], borderWidth: 1 }] },
    options: baseOptions({ interaction: { mode: 'nearest', intersect: true }, layout: { padding: { right: 14 } },
      scales: { x: { type: 'linear', offset: false, title: axisTitle(xt), ticks: { font: { size: 14 }, callback: (v) => Number(v).toFixed(2) } },
        y: { beginAtZero: true, title: axisTitle('values'), afterFit: (s) => { s.width = 64; }, ticks: { precision: 0, font: { size: 13 } } } },
      plugins: { legend: { display: false } } }),
  });
  rawChart = register(hist($('rawChart'), 'weight value (one hospital, before protection)'), (ch, c) => { const d = ch.data.datasets[0]; d.backgroundColor = c.hosp[0]; d.borderColor = c.panel; });
  aggChart = register(hist($('aggChart'), 'weight value (the combined model)'), (ch, c) => { const d = ch.data.datasets[0]; d.backgroundColor = c.accent; d.borderColor = c.panel; });
}

async function loadInspect(name, label) {
  const seq = ++inspectSeq;
  try {
    const d = await getJSON(`/api/inspect/${encodeURIComponent(name)}`);
    if (seq !== inspectSeq) return;   // a newer run/source started meanwhile
    renderInspect(d, label);
  } catch (err) { if (seq === inspectSeq) $('seesSource').textContent = 'Could not load the captured data: ' + err.message; }
}

function renderInspect(d, label) {
  if (!d.ready) { $('seesSource').textContent = 'Waiting for the capture of round 1 …'; return; }
  const info = d.info, mod = info.mod_range;
  lastInspect = { d, label }; $('seesSource').innerHTML = seesSourceHtml();
  renderHeroStrip(d);
  const n = Number(info.plaintext_arrays_out), arrays = info.masked_shapes ? info.masked_shapes.length - 1 : null;
  const badge = $('badge'); badge.className = 'badge' + (n > 0 ? ' bad' : '');
  badge.innerHTML = `Plaintext arrays leaving the hospital: <b>${n}</b><small>${info.secagg ? 'SecAgg+ on: only the masked vector is sent.' : 'SecAgg+ was off in this run: the plain weight arrays leave the hospital.'}${arrays && info.secagg ? ` With SecAgg off this counter shows ${arrays} (one per weight array).` : ''}</small>`;
  const stats = [];
  // top: unmasked quantized update
  const q = d.quantized_plain;
  const top = plainQChart.data.datasets[0];
  if (q) {
    const mid = (q.min + q.max) / 2, tot = q.count;
    top.data = [{ x: mid, y: tot }]; top.barThickness = 4; top.maxBarThickness = 4;
    plainQChart.options.scales.y.max = Math.ceil(tot * 1.1);
    stats.push(`<b>Without masking:</b> all ${tot} values lie between ${nf.format(q.min)} and ${nf.format(q.max)}: a stretch only ${((q.max - q.min) / mod * 100).toFixed(4)}% of the range wide, sitting ${(q.min / mod * 100).toFixed(2)}% from the left end. The bar is drawn 4 px wide so you can see it. <i>This view is a close approximation:</i> real SecAgg+ rounds each value randomly (stochastic rounding), so every value can differ by ±1 out of about ${nf.format(info.quant_range)} levels; the masked data in the chart below is the real capture.`);
  } else { top.data = []; stats.push('<b>Without masking:</b> not available for this capture.'); }
  plainQChart.update('none');
  // bottom: masked vector
  const md = maskedChart.data.datasets[0];
  if (d.masked) {
    const body = d.masked.values.slice(1), bins = 16, h = histValues(body, 0, mod, bins);   // 16 slices: the same slices the evenness test uses
    md.data = h.centers.map((x, i) => ({ x, y: h.counts[i] }));
    md.barThickness = undefined; md.maxBarThickness = undefined; md.barPercentage = 1; md.categoryPercentage = 1;
    const expected = body.length / bins;
    maskedChart.options.scales.y.max = Math.max(...h.counts, Math.ceil(expected * 2)) + 2;
    maskedChart.options.plugins.expected = Object.assign({}, maskedChart.options.plugins.expected, { value: expected, label: `perfectly even would be ${expected.toFixed(1)} per bin` });
    const m = d.masked, uniform = m.chi2_16_bins < m.chi2_p001_threshold;
    stats.push(`<b>With masking:</b> the ${body.length} model values are spread across all ${bins} equal slices of the range (${Math.min(...h.counts)} to ${Math.max(...h.counts)} per slice; a perfectly even spread would be ${(body.length / bins).toFixed(1)}). Evenness test (χ² over the same ${bins} slices): ${m.chi2_16_bins.toFixed(1)} against a threshold of ${m.chi2_p001_threshold} at 0.1% significance, so the vector is ${uniform ? '<b>consistent with uniformly random numbers</b>' : '<b>not consistent with uniform</b>'}. The first slot (an example counter) is left out.`);
  } else { md.data = []; stats.push('<b>With masking:</b> nothing was masked in this run (SecAgg+ off).'); }
  maskedChart.update('none');
  $('seesStats').innerHTML = stats.join('<br>');
  // raw + aggregate on one common range
  if (d.plain && d.aggregate) {
    const lim = Math.max(...d.plain.values.map(Math.abs), ...d.aggregate.values.map(Math.abs)) * 1.02, bins = 24;
    for (const [ch, vals] of [[rawChart, d.plain.values], [aggChart, d.aggregate.values]]) {
      const h = histValues(vals, -lim, lim, bins);
      ch.data.datasets[0].data = h.centers.map((x, i) => ({ x, y: h.counts[i] })); ch.data.datasets[0].barPercentage = 1; ch.data.datasets[0].categoryPercentage = 1;
      ch.options.scales.x.min = -lim; ch.options.scales.x.max = lim; ch.update('none');
    }
  }
}

// ============================================================ hero cipher strip
// 273 ticks, one per model value, placed on the number line 0 ... 2^32. Unmasked they sit in one spot; masked they fill the range.
// Plain positions are the same close approximation as the "without masking" chart: the raw weights mapped linearly into quantized_plain's [min, max].
const hero = { plain: null, masked: null, t0: 0, raf: 0, progress: 1 };
const frac = (i) => { const x = Math.sin(i * 12.9898 + 4.1414) * 43758.5453; return x - Math.floor(x); };   // fixed pseudo-random tick heights
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

function renderHeroStrip(d) {
  const empty = $('heroEmpty'), cv = $('heroStrip');
  hero.plain = hero.masked = null; cancelAnimationFrame(hero.raf);
  const q = d && d.ready && d.quantized_plain, w = d && d.plain && d.plain.values;
  $('heroReplay').hidden = true;
  if (!q || !w || !w.length) {
    empty.hidden = false; cv.style.visibility = 'hidden';
    $('heroState').textContent = 'Without masking'; $('heroState').className = '';
    return;
  }
  empty.hidden = true; cv.style.visibility = 'visible';
  const mod = d.info.mod_range, lo = Math.min(...w), span = (Math.max(...w) - lo) || 1;
  hero.plain = w.map((v) => (q.min + ((v - lo) / span) * (q.max - q.min)) / mod);
  hero.masked = d.masked ? d.masked.values.slice(1).map((v) => v / mod) : null;
  cv.setAttribute('aria-label', hero.masked
    ? `Cipher strip: the hospital's ${w.length} model values. Without masking they all sit within ${((q.max - q.min) / mod * 100).toFixed(3)} percent of the number line; with masking they are spread across the whole range.`
    : `Cipher strip: the hospital's ${w.length} model values, all within ${((q.max - q.min) / mod * 100).toFixed(3)} percent of the number line. SecAgg+ was off, so nothing is masked.`);
  if (!hero.masked) { hero.progress = 0; drawHero(); return; }
  $('heroReplay').hidden = false;
  if (REDUCED) { hero.progress = 1; drawHero(); syncHeroBtn(); return; }
  playHero();
}
function playHero() {
  cancelAnimationFrame(hero.raf);
  hero.t0 = performance.now() + 700;   // hold the unmasked state for 0.7 s, then mask once
  const tick = (now) => { hero.progress = Math.min(1, Math.max(0, (now - hero.t0) / 1800)); drawHero(); if (hero.progress < 1) hero.raf = requestAnimationFrame(tick); };
  hero.progress = 0; drawHero(); hero.raf = requestAnimationFrame(tick);
}
// reduced motion: the button flips between the two states instead of animating
function syncHeroBtn() { if (REDUCED) $('heroReplay').textContent = hero.progress >= 1 ? 'Show without masking' : 'Show with masking'; }
$('heroReplay').addEventListener('click', () => {
  if (!hero.masked) return;
  if (REDUCED) { hero.progress = hero.progress >= 1 ? 0 : 1; drawHero(); syncHeroBtn(); } else playHero();
});

function drawHero() {
  const cv = $('heroStrip'); if (!cv || !hero.plain) return;
  const dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight; if (!W || !H) return;
  if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); }
  const ctx = cv.getContext('2d'), c = C(), padX = 6, axisH = 22, n = hero.plain.length, bw = Math.max(2, Math.min(4, W / n * 0.6));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
  const top = 6, bottom = H - axisH, plotW = W - 2 * padX;
  ctx.fillStyle = c.muted; ctx.font = `400 12px ${FONT}`; ctx.textBaseline = 'top';
  ctx.strokeStyle = c.grid; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(padX, bottom + 0.5); ctx.lineTo(W - padX, bottom + 0.5); ctx.stroke();
  ctx.textAlign = 'left'; ctx.fillText('0', padX, bottom + 6);
  ctx.textAlign = 'center'; ctx.fillText('½', padX + plotW / 2, bottom + 6);
  ctx.textAlign = 'right'; ctx.fillText('2³²', W - padX, bottom + 6);
  const p = hero.progress, st = 0.45;                                   // st: share of the morph used to stagger the ticks
  for (let i = 0; i < n; i++) {
    const lt = hero.masked ? ease(Math.min(1, Math.max(0, (p - (i / n) * st) / (1 - st)))) : 0;
    const x = padX + plotW * (hero.plain[i] + ((hero.masked ? hero.masked[i] : hero.plain[i]) - hero.plain[i]) * lt);
    const h = (0.3 + 0.7 * frac(i)) * (bottom - top);
    ctx.globalAlpha = 0.92; ctx.fillStyle = lt > 0.5 ? c.lockFill : c.bad;
    ctx.fillRect(x - bw / 2, bottom - h, bw, h);
  }
  ctx.globalAlpha = 1;
  const masked = p >= 1 && hero.masked, label = masked ? 'With SecAgg+ masking' : 'Without masking';
  if ($('heroState').textContent !== label) $('heroState').textContent = label;
  $('heroState').className = masked ? 'locked' : '';
  $('heroCap').textContent = masked
    ? 'The same 273 values as the server actually receives them: spread across the whole range, indistinguishable from random numbers.'
    : "One hospital's 273 update values, as positions on the number line 0 to 2³². Unmasked, they sit in one spot, so the server could read each one.";
}
new ResizeObserver(() => drawHero()).observe($('heroStrip'));

// ============================================================ nav scrollspy
{
  const links = [...document.querySelectorAll('#mainNav a')], secs = links.map((a) => document.querySelector(a.getAttribute('href')));
  const setCur = (id) => links.forEach((a) => { if (a.getAttribute('href') === '#' + id) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
  const vis = new Map();
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => vis.set(e.target.id, e.isIntersecting ? e.intersectionRatio : 0));
    let best = null, bestR = 0; vis.forEach((r, id) => { if (r > bestR) { best = id; bestR = r; } });
    setCur(best);
  }, { rootMargin: '-80px 0px -45% 0px', threshold: [0, 0.1, 0.25, 0.5, 0.75, 1] });
  secs.forEach((x) => x && io.observe(x));
}

// ============================================================ panel 3: privacy vs accuracy
let trChart = null, sweeps = null;
const NODP_X = 1000;

// FedAvg and FedProx have the same ε, so they would hide each other. Their points are drawn 7 px apart; the data coordinate stays the true ε.
const nudgePlugin = { id: 'nudge', afterUpdate(chart) {
  chart.data.datasets.forEach((d, i) => { if (d.pxOffset) chart.getDatasetMeta(i).data.forEach((pt) => { pt.x += d.pxOffset; }); });
} };
const whiskerPlugin = { id: 'whiskers', afterDatasetsDraw(chart) {
  const { ctx, scales: { y } } = chart;
  chart.data.datasets.forEach((d, i) => {
    if (!d.stds || !chart.isDatasetVisible(i)) return;
    const meta = chart.getDatasetMeta(i); ctx.save(); ctx.strokeStyle = d.borderColor; ctx.lineWidth = 2;
    d.data.forEach((p, k) => {
      const px = meta.data[k].x, y1 = y.getPixelForValue(p.y - d.stds[k]), y2 = y.getPixelForValue(p.y + d.stds[k]);
      ctx.beginPath(); ctx.moveTo(px, y1); ctx.lineTo(px, y2); ctx.moveTo(px - 5, y1); ctx.lineTo(px + 5, y1); ctx.moveTo(px - 5, y2); ctx.lineTo(px + 5, y2); ctx.stroke();
    });
    ctx.restore();
  });
} };

function sweepGroups() { return sweeps.groups.filter((g) => g.n_seeds >= 2); }   // the 1-seed SECAGG=0 timing runs are not a sweep point

function buildTrChart() {
  const gs = sweepGroups();
  const epsVals = [...new Set(gs.filter((g) => g.mean_epsilon_max !== null).map((g) => g.mean_epsilon_max))].sort((a, b) => a - b);
  const noiseOf = (e) => (gs.find((g) => g.mean_epsilon_max === e) || {}).noise;
  const ticksAt = epsVals.concat([NODP_X]);
  const central = gs.length ? gs[0].mean_central_acc : null;
  const defs = [];
  for (const strat of ['fedavg', 'fedprox']) for (const sec of ['off', 'on']) {
    const pts = gs.filter((g) => g.strategy === strat && (sec === 'on' ? g.source === 'step4' && g.secagg === 1 : g.source === 'step3')).sort((a, b) => (a.mean_epsilon_max ?? 1e9) - (b.mean_epsilon_max ?? 1e9));
    defs.push({ strat, sec, label: `${strat === 'fedavg' ? 'FedAvg' : 'FedProx'}, SecAgg ${sec}`, key: `${strat}|${sec}`,
      data: pts.map((g) => ({ x: g.mean_epsilon_max ?? NODP_X, y: g.mean_fed_acc, g })), stds: pts.map((g) => g.std_fed_acc) });
  }
  const datasets = defs.map((d) => ({ label: d.label, data: d.data, stds: d.stds, strat: d.strat, sec: d.sec, pxOffset: d.strat === 'fedavg' ? -7 : 7, showLine: d.sec === 'on', borderWidth: 2.5,
    pointStyle: d.strat === 'fedavg' ? 'circle' : 'triangle', pointRadius: d.sec === 'on' ? 6 : 12, pointHoverRadius: d.sec === 'on' ? 8 : 14, pointBorderWidth: d.sec === 'on' ? 2 : 3 }));
  datasets.push({ label: 'Centralized (all data pooled)', data: central === null ? [] : [{ x: 8, y: central }, { x: 1500, y: central }], borderDash: [8, 6], borderWidth: 3, pointRadius: 0, showLine: true,
    endLabel: central === null ? '' : `centralized ${pct(central)}`, strat: 'central' });
  const ys = gs.flatMap((g) => [g.mean_fed_acc - g.std_fed_acc, g.mean_fed_acc + g.std_fed_acc]).concat(central ? [central] : []);
  trChart = register(new Chart($('trChart'), {
    type: 'scatter', data: { datasets },
    options: baseOptions({
      interaction: { mode: 'nearest', intersect: true },
      layout: { padding: { right: 12, top: 8 } },
      scales: {
        x: { type: 'logarithmic', min: 8, max: 1500, title: axisTitle('Privacy budget ε of the worst-off hospital: left = stronger privacy'),
          afterBuildTicks: (ax) => { ax.ticks = ticksAt.map((value) => ({ value })); },
          ticks: { font: { size: 14 }, callback: (v) => (v === NODP_X ? ['no DP', 'noise 0'] : [`ε ${v < 100 ? v.toFixed(1) : Math.round(v)}`, `noise ${noiseOf(v)}`]) } },
        y: { min: Math.floor((Math.min(...ys) - 0.01) * 50) / 50, max: Math.ceil((Math.max(...ys) + 0.01) * 50) / 50,
          title: axisTitle('Accuracy (mean of 5 seeds, ±1 std)'), ticks: { callback: (v) => pct(v, 0), font: { size: 14 } } },
      },
      plugins: { legend: { display: false }, tooltip: { callbacks: {
        title: () => '',
        label: (c) => { const g = c.raw.g; if (!g) return `${c.dataset.label}: ${pct(c.parsed.y, 2)}`;
          return [`${g.strategy === 'fedavg' ? 'FedAvg' : 'FedProx'}, SecAgg ${g.secagg ? 'on' : 'off'}, noise ${g.noise}`,
            `ε ${g.mean_epsilon_max === null ? '∞ (no DP)' : g.mean_epsilon_max.toFixed(1)}`, `accuracy ${pct(g.mean_fed_acc, 2)} ± ${pct(g.std_fed_acc, 2)} (${g.n_seeds} seeds)`]; } } } },
    }),
    plugins: [nudgePlugin, whiskerPlugin, endLabelPlugin],
  }), (ch, c) => ch.data.datasets.forEach((d) => {
    const col = d.strat === 'fedavg' ? c.fedavg : d.strat === 'fedprox' ? c.fedprox : c.text;
    d.borderColor = col; d.pointBorderColor = col; d.backgroundColor = d.sec === 'off' ? 'transparent' : col; d.pointBackgroundColor = d.sec === 'off' ? 'transparent' : col;
  }));
  applyTrFilters();
}

function applyTrFilters() {
  if (!trChart) return;
  const on = {}; document.querySelectorAll('#trFilters input').forEach((i) => { on[i.dataset.f] = i.checked; });
  trChart.data.datasets.forEach((d, i) => { if (d.strat === 'central') return; trChart.setDatasetVisibility(i, on[d.strat] && on[d.sec]); });
  trChart.update('none');
}
$('trFilters').addEventListener('change', applyTrFilters);

function renderSweeps(data) {
  sweeps = data; const h = data.headline, gs = sweepGroups();
  const m = /^(\w+)_runs\.jsonl: secagg=(\d), strategy=(\w+), noise=([\d.]+)/.exec(h.source || '');
  const g = m ? gs.find((x) => x.source === m[1] && String(x.secagg) === m[2] && x.strategy === m[3] && String(x.noise) === String(Number(m[4]))) : null;
  if (h.gap_points === null) { $('hlMain').textContent = 'No sweep results found.'; $('trHeadline').textContent = 'No sweep results found.'; }
  else {
    const main = `Within ${h.gap_points.toFixed(1)} accuracy points (${h.relative_gap_pct.toFixed(1)}%) of a centralized model, at ε ≈ ${h.epsilon.toFixed(1)}, without sharing patient data.`;
    $('hlMain').textContent = main;
    const cfg = g ? `${g.strategy === 'fedavg' ? 'FedAvg' : 'FedProx'}, DP noise ${g.noise}, SecAgg ${g.secagg ? 'on' : 'off'}` : h.source;
    const accs = g ? ` Federated ${pct(g.mean_fed_acc, 2)} vs centralized ${pct(g.mean_central_acc, 2)} (mean of ${g.n_seeds} seeds).` : '';
    const sp = g ? g.std_fed_acc * 100 : null;
    const spread = sp === null ? '' : h.gap_points <= sp ? ` The gap is within the seed-to-seed spread of ±${sp.toFixed(1)} points, so it is not a proven difference.` : ` For scale: results move by ±${sp.toFixed(1)} points between seeds.`;
    const band = h.epsilon > 10 ? ' ε above 10 is in the weak band of the ε chart: the hospitals are small, so the privacy cost shows up in ε.' : '';
    $('hlSub').textContent = `Most private configuration we ran (${cfg}), not the most accurate.${accs}${spread}${band}`;
    $('trHeadline').innerHTML = `<b>${esc(main)}</b><small>This is the most private configuration (lowest ε), not the best-looking one. Computed from <code>${esc(h.source)}</code> by dashboard/sweeps.py.${esc(accs)}${esc(spread)}</small>`;
    if (g) {
      const spread = g.std_fed_acc * 100;
      $('seedLimit').innerHTML = h.gap_points <= spread
        ? `<b>Small gap, big spread.</b> The headline gap (${h.gap_points.toFixed(1)} points) is no larger than the seed-to-seed spread (±${spread.toFixed(1)} points, <em>standard deviation</em>), so read it as “close to centralized”, not “proven worse”.`
        : `<b>Seed spread.</b> Results move by about ±${spread.toFixed(1)} points between random seeds; the test set is small.`;
    }
  }
  buildTrChart();
  const tbl = $('trTable'); tbl.textContent = '';
  const mk = (tag, texts, parent) => { const tr = document.createElement('tr'); texts.forEach((t) => { const c = document.createElement(tag); c.textContent = t; tr.appendChild(c); }); parent.appendChild(tr); };
  const th = document.createElement('thead'), tb = document.createElement('tbody'); tbl.append(th, tb);
  mk('th', ['SecAgg', 'strategy', 'noise', 'ε (max)', 'accuracy', 'std', 'centralized', 'seeds'], th);
  gs.forEach((x) => mk('td', [x.source === 'step4' ? 'on' : 'off', x.strategy, String(x.noise), x.mean_epsilon_max === null ? '∞' : x.mean_epsilon_max.toFixed(1),
    pct(x.mean_fed_acc, 2), '±' + pct(x.std_fed_acc, 2), pct(x.mean_central_acc, 2), String(x.n_seeds)], tb));
}

// ============================================================ boot
async function boot() {
  makeAccChart(); makeEpsChart(); makeInspectCharts();
  restyleAll();
  if (document.fonts) document.fonts.load(`400 15px ${FONT}`).then(() => document.fonts.ready).then(restyleAll).catch(() => {});   // canvas text needs Plex loaded before it is drawn
  renderHeroStrip(null);
  try { const g = (await getJSON('/api/replays/golden_run')).events.find((e) => e.type === 'baseline'); if (g) { DEFAULT_NAMES = g.hospitals; S.hospitals = g.hospitals.slice(); } } catch (e) { /* keep placeholders */ }
  const jobs = [];
  jobs.push(getJSON('/api/sweeps').then(renderSweeps).catch((e) => {
    $('hlMain').textContent = 'Sweep results unavailable.'; $('hlSub').textContent = e.message; $('trHeadline').textContent = 'Sweep results unavailable: ' + e.message;
  }));
  jobs.push(getJSON('/api/replays').then((list) => {
    const sel = $('replaySel'); sel.innerHTML = '';
    list.forEach((r) => { const o = document.createElement('option'); o.value = r.name; o.textContent = r.kind === 'replay' ? `${r.name} (saved recording)` : `${r.name} (your earlier run)`; sel.appendChild(o); });
  }).catch(() => {}));
  let attached = false;
  try { attached = await attachCurrent(); } catch (e) { /* no run to attach */ }
  if (!attached) {
    await showPreview();
    loadInspect('golden_run', 'recorded golden run');
  }
  await Promise.all(jobs);
  restyleAll();
}
boot();
