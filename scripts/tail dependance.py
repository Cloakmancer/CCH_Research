import numpy as np
import pyvinecopulib as pv
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
peak   = rng.gamma(2, 500, 500)
volume = peak * rng.uniform(0.4, 1.6, 500)
pseudo_obs = pv.to_pseudo_obs(np.column_stack([peak, volume]))

u, v = pseudo_obs[:, 0], pseudo_obs[:, 1]

# Empirical upper tail dependence coefficient
def lambda_U_empirical(u, v, q_range=None):
    """λ_U(t) = P(V > t | U > t) for t → 1"""
    if q_range is None:
        q_range = np.linspace(0.80, 0.99, 40)
    lam = []
    for t in q_range:
        mask = (u > t) & (v > t)
        total_above = np.mean(u > t)
        lam.append(np.mean(mask) / total_above if total_above > 0 else np.nan)
    return np.array(q_range), np.array(lam)

t_vals, lam_u = lambda_U_empirical(u, v)

# Also check lower tail
def lambda_L_empirical(u, v, q_range=None):
    if q_range is None:
        q_range = np.linspace(0.01, 0.20, 40)
    lam = []
    for t in q_range:
        mask = (u < t) & (v < t)
        total_below = np.mean(u < t)
        lam.append(np.mean(mask) / total_below if total_below > 0 else np.nan)
    return np.array(q_range), np.array(lam)

t_low, lam_l = lambda_L_empirical(u, v)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(t_vals, lam_u, "o-", ms=3)
axes[0].set_xlabel("Threshold t")
axes[0].set_ylabel("λ_U(t)")
axes[0].set_title("Upper tail dependence")

axes[1].plot(t_low, lam_l, "o-", ms=3, color="#D85A30")
axes[1].set_xlabel("Threshold t")
axes[1].set_ylabel("λ_L(t)")
axes[1].set_title("Lower tail dependence")
plt.tight_layout(); plt.show()

# If λ_U → 0: Frank/Gaussian/Clayton; if > 0: Gumbel/Joe/BB
print(f"λ_U (mean, t>0.90): {np.nanmean(lam_u[t_vals>0.90]):.3f}")