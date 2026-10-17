# Event improvement 1: TLS on gRPC (step 6 deployment)

## Goal
Close the limit "gRPC is insecure (no TLS)": encrypt SuperLink <-> SuperNode (Fleet API), CLI/dashboard -> SuperLink (Control API)
and SuperLink -> its ServerApp process (Runtime API). Playbook 1.2 option 1. Chosen by the user on 2026-10-17.

## Facts checked in the installed Flower 1.37 (not from memory)
- `flower-superlink --ssl-certfile --ssl-keyfile --ssl-ca-certfile`: one cert for Fleet, Control and Runtime APIs; `--insecure` overrides.
- `flower-supernode --root-certificates <ca.pem>` (server auth only, not mTLS).
- CLI `$FLWR_HOME/config.toml`: `root-certificates = "<path>"` (must not be combined with `insecure = true`).
- Flower itself passes the CA to the `flower-superexec` children it spawns; they connect to `resolve_bind_address(...)` = 127.0.0.1
  for 0.0.0.0. So the server cert SANs = `superlink`, `localhost`, `127.0.0.1`, `::1`.
- `cryptography` 46.0.7 is in the venv and in the image (Flower dependency): no new dependency, no openssl needed.

## Files (worktree `../IBM DATATHON-tls`, branch `feature/grpc-tls` from origin/main; the flip+boost session owns this checkout)
- NEW `deploy/gen_certs.py`: self-signed CA + server cert/key (SANs above, 365 days) into `deploy/certs/` (gitignored, private key
  never committed). Skips existing files unless `--force`. Python + cryptography only (works on Windows and inside the image).
- `deploy/docker-compose.yml` + `docker-compose.mixed.yml`: superlink `--ssl-*` with `certs/` mounted read-only; each supernode gets
  ONLY `ca.crt` mounted and `--root-certificates`; dashboard gets `ca.crt`.
- `deploy/flwr_home/config.toml`: `root-certificates = "/certs/ca.crt"` instead of `insecure = true`.
- NEW `deploy/docker-compose.insecure.yml`: override file = the old insecure commands (demo fallback, one flag away).
- `run_step6_local.py`: env `TLS` (default 1): generates certs in its work dir and passes the same flags; `TLS=0` = old behaviour.
- `test_step6_deploy.py`: add (1) TLS run == insecure run exactly (acc, F1, per-hospital, eps; seed 0, SECAGG 0, 3 rounds),
  (2) negative: a SuperNode started with `--insecure` against the TLS SuperLink never joins (run does not start / times out).
- Docs: CLAUDE.md step 6 limits, `deploy/LINUXONE.md` (gen_certs step before `compose up`), playbook 6.4 limits + 3 results row.
- dashboard/server.py: NO change (deploy mode already reads FLWR_HOME/config.toml) -> no collision with the flip+boost session.

## Risks
- A cert without the right SAN fails only at connect time (quiet hang with retries): the negative + positive tests catch it.
- Mixed amd64/s390x and LinuxONE untested with TLS until the event VM; the insecure override is the fallback.
- Docker engine is not running on the laptop now: Docker verification needs Docker Desktop started (else only the native path is verified).

## Verification
`py deploy/gen_certs.py`; `TLS=1 run_step6_local.py rounds=3 secagg=1`; `test_step6_deploy.py` (~20 min); Docker `compose up`
+ one dashboard run if Docker starts; `openssl`-free check that port 9092 refuses a plaintext gRPC client.

## Routing card
| Phase | Agent | Model | Effort | Why |
|---|---|---|---|---|
| Build + tests | this session | opus (current) | medium | small, but cert/SAN failures are quiet |
| Review | subagent | sonnet | high | independent check of compose mounts and key handling |
Codex/Antigravity handoffs: none. Switch needed: none.
