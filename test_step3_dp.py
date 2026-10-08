"""Checks for step 3. Run:  .venv\\Scripts\\python.exe test_step3_dp.py"""
import numpy as np
import torch

import step3_heart_dp as s3

d = s3.DATA[0]


def trained_weights(mu, seed=7, noise=1.0, perturb=0):
    torch.manual_seed(0)
    m = s3.Net()  # identical "global" weights each call
    torch.manual_seed(perturb)  # global RNG state at training time: result must not depend on it
    s3.train_dp(m, d["X_tr"], d["y_tr"], s3.LOCAL_EPOCHS, mu, noise, s3.CLIP, seed)
    return torch.cat([p.detach().flatten() for p in m.parameters()])


# 1. same seed + noise: identical result (so any difference below is due to mu alone)
a, b = trained_weights(0.0), trained_weights(0.0)
assert torch.equal(a, b), "DP training is not deterministic for a fixed seed"

# 2. prox term changes the weights, and a larger mu pulls them closer to w_global
torch.manual_seed(0)
w0 = torch.cat([p.detach().flatten() for p in s3.Net().parameters()])
w_mu0, w_mu01, w_mu5 = trained_weights(0.0), trained_weights(0.1), trained_weights(5.0)
assert not torch.allclose(w_mu0, w_mu01), "mu=0.1 did not change the weights vs mu=0"
dist = lambda w: (w - w0).norm().item()
assert dist(w_mu5) < dist(w_mu0), "large mu should stay closer to w_global"
print(f"mu check OK: |w-w_global| mu=0: {dist(w_mu0):.4f}, mu=0.1: {dist(w_mu01):.4f}, mu=5: {dist(w_mu5):.4f}")

# 2b. Poisson batches + noise depend only on `seed`, not on the global RNG (even at noise 0)
assert torch.equal(trained_weights(0.0, noise=0.0, perturb=1), trained_weights(0.0, noise=0.0, perturb=99))
print("seed determinism OK")

# 3. epsilon: grows with rounds, shrinks with noise
n = len(d["y_tr"])
eps_r = [s3.epsilon_after(n, r, noise=1.0) for r in (1, 5, 10, 20)]
assert all(x < y for x, y in zip(eps_r, eps_r[1:])), eps_r
eps_n = [s3.epsilon_after(n, 20, noise=z) for z in (0.5, 1.0, 2.0)]
assert all(x > y for x, y in zip(eps_n, eps_n[1:])), eps_n
print(f"epsilon vs rounds (noise 1, n={n}): {[round(e, 2) for e in eps_r]}")
print(f"epsilon vs noise  (20 rounds)     : {dict(zip((0.5, 1.0, 2.0), [round(e, 2) for e in eps_n]))}")

# 4. cross-check: deterministic formula vs the live PrivacyEngine accountant after one real round
torch.manual_seed(0)
engine, n_steps = s3.train_dp(s3.Net(), d["X_tr"], d["y_tr"], s3.LOCAL_EPOCHS, 0.0, 1.0, s3.CLIP, 1)
live = engine.accountant.get_epsilon(s3.DELTA)
mine = s3.epsilon_after(n, 1, noise=1.0)
q, spe = s3.sample_rate_and_steps(n)
assert abs(live - mine) < 1e-9, (live, mine)
assert engine.accountant.history[-1][1] == q and engine.accountant.history[-1][2] == s3.LOCAL_EPOCHS * spe == s3.LOCAL_EPOCHS * n_steps
print(f"accountant cross-check OK: live eps {live:.6f} == formula {mine:.6f} (q={q:.4f}, steps={s3.LOCAL_EPOCHS * spe})")
print("ALL OK")
