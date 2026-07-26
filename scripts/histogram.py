import numpy as np
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# --- 1. Frequency Histogram (Student Heights) ---
# 30 students, mean=165cm, std=7cm
heights = np.random.normal(loc=165, scale=7, size=30)
# Define equal bins of 5 cm intervals from 145 to 185
bins_height = np.arange(145, 190, 5)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(heights, bins=bins_height, edgecolor='black', color='skyblue', rwidth=0.9)
ax.set_title('Frequency Histogram: Student Heights (Equal Bins)')
ax.set_xlabel('Height (cm)')
ax.set_ylabel('Frequency (Number of Students)')
ax.set_xticks(bins_height)
fig.tight_layout()
fig.savefig('histogram_frequency.png')
plt.close(fig)

# --- 2. Relative Frequency Histogram (Exam Scores: Class A vs Class B) ---
# Class A: 30 students, Class B: 120 students. Both have similar distribution shape.
scores_A = np.random.normal(loc=72, scale=12, size=30)
scores_B = np.random.normal(loc=72, scale=12, size=120)
bins_scores = np.arange(40, 110, 10)

# We want to show side-by-side or compare Raw vs Relative
# Let's make a 1x2 subplot to show why relative frequency is needed
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Raw Frequency comparison
ax1.hist([scores_A, scores_B], bins=bins_scores, edgecolor='black', 
         label=['Class A (n=30)', 'Class B (n=120)'], color=['orange', 'lightgreen'])
ax1.set_title('Raw Frequency: Misleading Comparison due to Class Size')
ax1.set_xlabel('Exam Scores')
ax1.set_ylabel('Frequency (Count)')
ax1.set_xticks(bins_scores)
ax1.legend()

# Relative Frequency comparison
# To get relative frequency (proportion), we use weights
weights_A = np.ones_like(scores_A) / len(scores_A)
weights_B = np.ones_like(scores_B) / len(scores_B)

ax2.hist([scores_A, scores_B], bins=bins_scores, weights=[weights_A, weights_B], 
         edgecolor='black', label=['Class A (n=30)', 'Class B (n=120)'], color=['orange', 'lightgreen'])
ax2.set_title('Relative Frequency: Fair Comparison of Distributions')
ax2.set_xlabel('Exam Scores')
ax2.set_ylabel('Relative Frequency (Proportion)')
ax2.set_xticks(bins_scores)
ax2.legend()

fig.tight_layout()
fig.savefig('histogram_relative_frequency.png')
plt.close(fig)

# --- 3. Frequency Density Histogram (Income Distribution with Unequal Bins) ---
# Generate heavily skewed income data (in thousands of dollars)
# E.g., lognormal distribution
income = np.random.lognormal(3.5, 0.8, 500) # scale to realistic thousands
# Filter or clip to realistic range for the example
income = income[income < 500]

# Unequal bins: 0-20k, 20-40k, 40-60k, 60-80k, 80-100k, 100-500k
bins_income = [0, 20, 40, 60, 80, 100, 500]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left plot: Misleading Raw Frequency with unequal bins
counts, bin_edges = np.histogram(income, bins=bins_income)
bin_centers = bin_edges[:-1] + np.diff(bin_edges)/2
bin_widths = np.diff(bin_edges)

# If we just plot counts with the actual wide bin without adjusting height, matplotlib's hist actually
# draws a massive area because the bar is wide AND tall. Let's see what happens if we plot raw frequency as bar heights over unequal intervals:
ax1.bar(bin_edges[:-1], counts, width=bin_widths, align='edge', edgecolor='black', color='salmon', alpha=0.7)
ax1.set_title('Raw Frequency with Unequal Bins (Misleading Area)')
ax1.set_xlabel('Income ($ Thousands)')
ax1.set_ylabel('Frequency (Count)')
ax1.set_xticks(bins_income)
ax1.set_xticklabels([f'{x}k' if x > 0 else '0' for x in bins_income], rotation=45)

# Right plot: Frequency Density (Count / Bin Width)
# Height = count / width
density = counts / bin_widths

ax2.bar(bin_edges[:-1], density, width=bin_widths, align='edge', edgecolor='black', color='teal', alpha=0.7)
ax2.set_title('Frequency Density (Height = Count ÷ Width)')
ax2.set_xlabel('Income ($ Thousands)')
ax2.set_ylabel('Frequency Density (Counts per $1k width)')
ax2.set_xticks(bins_income)
ax2.set_xticklabels([f'{x}k' if x > 0 else '0' for x in bins_income], rotation=45)

fig.tight_layout()
fig.savefig('histogram_frequency_density.png')
plt.close(fig)

print("Plots generated successfully!")