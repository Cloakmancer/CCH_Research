import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Major Probability Distributions", fontsize=16, fontweight='bold')

# ── 1. NORMAL ──────────────────────────────────────────────────────────────────
ax = axes[0, 0]
mu, sigma = 170, 7  # mean height, std dev
x = np.linspace(140, 200, 300)
pdf = stats.norm.pdf(x, mu, sigma)

ax.plot(x, pdf, 'b-', linewidth=2)
ax.fill_between(x, pdf, where=(x >= 163) & (x <= 177), alpha=0.3, color='blue', label='±1σ (68%)')
ax.fill_between(x, pdf, where=(x >= 177) & (x <= 184), alpha=0.2, color='green')
ax.fill_between(x, pdf, where=(x >= 156) & (x <= 163), alpha=0.2, color='green', label='±2σ (95%)')
ax.axvline(mu, color='red', linestyle='--', label=f'μ={mu}')
ax.set_title("Normal Distribution\nQ: What % of people are between 163–177cm?")
ax.set_xlabel("Height (cm)")
ax.set_ylabel("Probability Density")
ax.legend(fontsize=8)

p_1sigma = stats.norm.cdf(177, mu, sigma) - stats.norm.cdf(163, mu, sigma)
ax.text(150, max(pdf)*0.6, f"P(163<X<177) = {p_1sigma:.3f}\n= {p_1sigma*100:.1f}%", fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat'))

# Formula
ax.text(150, max(pdf)*0.2,
        r"$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$",
        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow'))

# ── 2. BINOMIAL ────────────────────────────────────────────────────────────────
ax = axes[0, 1]
n, p = 20, 0.3  # 20 free throws, 30% success rate
k = np.arange(0, n+1)
pmf = stats.binom.pmf(k, n, p)

bars = ax.bar(k, pmf, color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.5)
# Highlight P(X >= 10)
for i, bar in enumerate(bars):
    if i >= 10:
        bar.set_color('orange')
        bar.set_alpha(0.9)

ax.set_title("Binomial Distribution\nQ: P(scoring ≥10 in 20 free throws, p=0.3)?")
ax.set_xlabel("Number of Successes")
ax.set_ylabel("Probability")

p_gte_10 = 1 - stats.binom.cdf(9, n, p)
ax.text(12, max(pmf)*0.8, f"P(X≥10) = {p_gte_10:.4f}\n= {p_gte_10*100:.2f}%", fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat'))

ax.text(0.5, max(pmf)*0.5,
        r"$P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$",
        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow'))

# ── 3. POISSON ─────────────────────────────────────────────────────────────────
ax = axes[1, 0]
lam = 4  # avg 4 customers per hour
k = np.arange(0, 16)
pmf = stats.poisson.pmf(k, lam)

bars = ax.bar(k, pmf, color='green', alpha=0.7, edgecolor='black', linewidth=0.5)
for i, bar in enumerate(bars):
    if i > 7:
        bar.set_color('red')
        bar.set_alpha(0.7)

ax.set_title("Poisson Distribution\nQ: P(more than 7 customers in an hour, λ=4)?")
ax.set_xlabel("Number of Events (k)")
ax.set_ylabel("Probability")

p_gt7 = 1 - stats.poisson.cdf(7, lam)
ax.text(8, max(pmf)*0.8, f"P(X>7) = {p_gt7:.4f}\n= {p_gt7*100:.2f}%", fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat'))

ax.text(8, max(pmf)*0.5,
        r"$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$",
        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow'))

# ── 4. EXPONENTIAL ─────────────────────────────────────────────────────────────
ax = axes[1, 1]
lam = 4  # same lambda — avg 4 customers/hr means avg wait = 1/4 hr = 15 min
x = np.linspace(0, 1.5, 300)  # in hours
pdf = stats.expon.pdf(x, scale=1/lam)

ax.plot(x, pdf, 'purple', linewidth=2)
ax.fill_between(x, pdf, where=(x <= 0.25), alpha=0.3, color='purple', label='P(X≤15min)')
ax.fill_between(x, pdf, where=(x > 0.5), alpha=0.2, color='red', label='P(X>30min)')

ax.set_title("Exponential Distribution\nQ: P(waiting >30 min if avg rate=4/hr)?")
ax.set_xlabel("Waiting Time (hours)")
ax.set_ylabel("Probability Density")
ax.legend(fontsize=8)

p_gt30 = 1 - stats.expon.cdf(0.5, scale=1/lam)
p_lt15 = stats.expon.cdf(0.25, scale=1/lam)
ax.text(0.6, max(pdf)*0.6,
        f"P(X>0.5hr) = {p_gt30:.4f}\n= {p_gt30*100:.1f}%\n\nP(X<0.25hr) = {p_lt15:.3f}\n= {p_lt15*100:.1f}%",
        fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat'))

ax.text(0.6, max(pdf)*0.2,
        r"$f(x) = \lambda e^{-\lambda x}$",
        fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow'))

plt.tight_layout()
plt.savefig("distributions.png", dpi=150, bbox_inches='tight')
plt.show()
print("Plot saved as distributions.png")
