"""
StatQuest concepts applied to a cascading-hazards example: daily rainfall.
Covers: histograms, probability distributions, normal distribution,
mean/median/mode, and the exponential distribution (return periods).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

np.random.seed(42)

# ---------------------------------------------------------------
# 1. Synthetic daily rainfall data (mm/day), skewed like real rainfall:
#    most days are dry/light rain, a few days are extreme storms.
#    A gamma distribution captures this "many small, few huge" shape,
#    which is much more realistic than a normal distribution for rainfall.
# ---------------------------------------------------------------
n_days = 3650  # ~10 years of daily data
rainfall = stats.gamma.rvs(a=0.6, scale=8, size=n_days)  # mm/day

# ---------------------------------------------------------------
# 2. Histogram — first thing you always do: look at the shape of the data
# ---------------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.hist(rainfall, bins=60, color="steelblue", edgecolor="white")
plt.title("Histogram of Daily Rainfall (10 years, synthetic)")
plt.xlabel("Rainfall (mm/day)")
plt.ylabel("Number of days")
plt.savefig("rainfall_histogram.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------
# 3. Mean vs Median vs Mode
#    In skewed data, mean gets pulled toward the extreme tail;
#    median stays representative of a "typical" day.
# ---------------------------------------------------------------
mean_val = np.mean(rainfall)
median_val = np.median(rainfall)
mode_val = stats.mode(np.round(rainfall, 0), keepdims=False).mode

print("=== Mean / Median / Mode ===")
print(f"Mean:   {mean_val:.2f} mm")
print(f"Median: {median_val:.2f} mm")
print(f"Mode:   {mode_val:.2f} mm")
print("-> Mean > Median here because a handful of extreme storm days pull it up.\n")

# ---------------------------------------------------------------
# 4. Normal distribution fit — does it actually fit rainfall well?
#    Spoiler: no, because rainfall is right-skewed and can't go negative,
#    but Normal assumes symmetry and allows negative values.
# ---------------------------------------------------------------
mu, sigma = stats.norm.fit(rainfall)
x = np.linspace(rainfall.min(), rainfall.max(), 500)
normal_pdf = stats.norm.pdf(x, mu, sigma)

plt.figure(figsize=(8, 5))
plt.hist(rainfall, bins=60, density=True, color="steelblue", edgecolor="white", alpha=0.6, label="Actual data")
plt.plot(x, normal_pdf, color="red", linewidth=2, label=f"Normal fit (μ={mu:.1f}, σ={sigma:.1f})")
plt.title("Rainfall Data vs Fitted Normal Distribution")
plt.xlabel("Rainfall (mm/day)")
plt.ylabel("Density")
plt.legend()
plt.savefig("rainfall_vs_normal.png", dpi=150, bbox_inches="tight")
plt.close()

print("=== Normal Distribution Fit ===")
print(f"Fitted Normal: mu={mu:.2f}, sigma={sigma:.2f}")
print("-> Visually (see rainfall_vs_normal.png) the red curve underestimates the")
print("   sharp peak at low rainfall and the long right tail of storm events.")
print("   This is why hazard magnitudes are usually modeled with skewed")
print("   distributions (gamma, log-normal, or extreme-value), not Normal.\n")

# ---------------------------------------------------------------
# 5. Exponential distribution — time between HEAVY rainfall events
#    Define "heavy rainfall" as a threshold exceedance (a simple hazard trigger),
#    then look at the gaps between such days -> this is a return-period calc.
# ---------------------------------------------------------------
threshold = np.percentile(rainfall, 95)  # top 5% of days = "heavy rainfall event"
heavy_days = np.where(rainfall > threshold)[0]
gaps = np.diff(heavy_days)  # days between consecutive heavy-rainfall events

rate_lambda = 1 / np.mean(gaps)  # exponential rate parameter
return_period_days = 1 / rate_lambda

plt.figure(figsize=(8, 5))
plt.hist(gaps, bins=30, density=True, color="darkorange", edgecolor="white", alpha=0.6, label="Actual gaps")
x2 = np.linspace(0, gaps.max(), 200)
plt.plot(x2, stats.expon.pdf(x2, scale=1/rate_lambda), color="black", linewidth=2, label="Exponential fit")
plt.title(f"Days Between Heavy Rainfall Events (>{threshold:.1f} mm)")
plt.xlabel("Gap between events (days)")
plt.ylabel("Density")
plt.legend()
plt.savefig("rainfall_return_period.png", dpi=150, bbox_inches="tight")
plt.close()

print("=== Exponential Distribution: Return Period ===")
print(f"Heavy rainfall threshold (95th percentile): {threshold:.2f} mm/day")
print(f"Number of heavy rainfall events in {n_days} days: {len(heavy_days)}")
print(f"Mean gap between events: {np.mean(gaps):.1f} days")
print(f"Estimated return period: ~{return_period_days:.1f} days "
      f"(~{return_period_days/365:.2f} years)")
print("-> This 'return period' concept (from the exponential/memoryless model)")
print("   is exactly what's used in engineering design (e.g. '100-year flood')")
print("   and is a building block for modeling cascading hazard recurrence.")
