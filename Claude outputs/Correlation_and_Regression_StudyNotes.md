# Day 4 — Correlation and regression

*2026-08-07*

One dataset runs through the whole page so the sections build on each other instead of
restarting each time. Companion interactive: **[Correlation & Regression, Played
With](interactive/correlation-and-regression.html){target=_blank}** — six live panels (drag a
scatter and watch r recompute, a guess-the-r calibration game, fit a regression line by hand
against the least-squares minimum, Anscombe's quartet, and a correlation-vs-causation gallery).

This page departs from the Concept/Bridge/Feynman skeleton the other three days use — it reads
more like a worked reference than a log entry, with its own table of contents below — because
that's the format that turned out to work better for retention here. Practice problems are
Section 6, not a separate page.

## How to use this

Read Sections 1–3 once, straight through, doing the arithmetic yourself before checking it
against the tables. Section 4 is the point of the exercise — it's where this stops being generic
statistics and becomes the next concrete step in the copula workflow (Project Status, Next
Actions 2–3). Section 6 is retrieval practice; do it a day later, not immediately after reading,
or you're testing your short-term memory instead of your understanding.

---

## 1. Correlation

### 1.1 What it is

**Correlation** measures the strength and direction of a *linear* association between two
variables. **Pearson's r** is the standard version:

$$r = \dfrac{\sum (x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum (x_i-\bar x)^2 \sum (y_i-\bar y)^2}}
= \dfrac{S_{xy}}{\sqrt{S_{xx}\,S_{yy}}}$$

Read the numerator first. $S_{xy}=\sum(x_i-\bar x)(y_i-\bar y)$ is the **covariance sum**: for
each point, multiply how far above/below average it is on x by how far above/below average it is
on y. If x and y tend to be above average *together* and below average *together*, most products
are positive and $S_{xy}$ is large and positive. If one tends to be high when the other is low,
$S_{xy}$ is negative. The denominator just rescales this into something bounded: dividing by the
two variables' own spreads makes r **unit-free** and confines it to $[-1, 1]$, no matter what
units x and y are measured in.

- $r = +1$: every point sits exactly on an upward-sloping line.
- $r = -1$: every point sits exactly on a downward-sloping line.
- $r = 0$: no *linear* trend (there can still be a strong nonlinear one — Section 1.4).

### 1.2 The dataset for this document

Six historic flood events at one gauge: peak discharge Q (m³/s) and total event volume V (Mm³).

| Event | Q (m³/s) | V (Mm³) |
|---|---|---|
| 1 | 420 | 190 |
| 2 | 610 | 230 |
| 3 | 380 | 150 |
| 4 | 750 | 260 |
| 5 | 540 | 250 |
| 6 | 690 | 300 |

$\bar Q = 565.0$, $\bar V = 230.0$.

### 1.3 Worked example — r by hand

| Event | Q | V | $Q-\bar Q$ | $V-\bar V$ | $(Q-\bar Q)(V-\bar V)$ | $(Q-\bar Q)^2$ | $(V-\bar V)^2$ |
|---|---|---|---|---|---|---|---|
| 1 | 420 | 190 | −145 | −40 | +5,800 | 21,025 | 1,600 |
| 2 | 610 | 230 | +45 | 0 | 0 | 2,025 | 0 |
| 3 | 380 | 150 | −185 | −80 | +14,800 | 34,225 | 6,400 |
| 4 | 750 | 260 | +185 | +30 | +5,550 | 34,225 | 900 |
| 5 | 540 | 250 | −25 | +20 | −500 | 625 | 400 |
| 6 | 690 | 300 | +125 | +70 | +8,750 | 15,625 | 4,900 |
| **Σ** | | | | | **34,400** | **107,750** | **14,200** |

So $S_{xy}=34{,}400$, $S_{xx}=107{,}750$, $S_{yy}=14{,}200$.

$$r = \frac{34{,}400}{\sqrt{107{,}750 \times 14{,}200}} = \frac{34{,}400}{\sqrt{1{,}530{,}050{,}000}}
= \frac{34{,}400}{39{,}116} = \mathbf{0.879}$$

Strong positive correlation — bigger peaks come with bigger volumes, which is exactly what you'd
expect physically (a bigger flood is bigger in more than one way at once). Notice event 5 has a
**negative** cross-product: it has below-average peak but above-average volume. One point doesn't
overturn a strong overall r, but it's a preview of Section 4.1 — Pearson r is an *average*
statement, and individual points can quietly disagree with it.

### 1.4 What r does not tell you

- **Not causation.** r is symmetric in x and y — it cannot distinguish "Q drives V" from "V drives
  Q" from "a third thing drives both." (Interactive panel 6 works three examples of exactly this.)
- **Not the whole shape.** Anscombe's quartet (interactive panel 5) is the canonical demonstration:
  four wildly different scatters, same r to three decimal places. r summarizes; it doesn't
  describe.
- **Not robust to one bad point.** A single high-leverage point can inflate or gut r (interactive
  panel 2). Always look at the scatter before trusting the number.
- **Not sensitive to nonlinear-but-monotonic relationships.** r can understate a relationship that
  is perfectly predictable but curved. This one matters enough to get its own section — see 3.1.

---

## 2. Simple linear regression

### 2.1 The model

$$y_i = \beta_0 + \beta_1 x_i + \varepsilon_i$$

$\beta_1$ is the slope — the average change in y per unit change in x. $\beta_0$ is the
intercept — the model's prediction for y when x = 0 (sometimes physically meaningless,
sometimes not; here it would be "expected volume of a zero-discharge flood," which is nonsense,
so don't over-interpret it — see the closing note in 2.3). $\varepsilon_i$ is everything the
straight line doesn't capture: measurement noise, other drivers, nonlinearity.

### 2.2 Least squares, derived

**Least squares** picks $\hat\beta_0, \hat\beta_1$ to minimize the total squared vertical
distance between the line and the points:

$$\mathrm{SSE}(\beta_0,\beta_1) = \sum_i \big(y_i - \beta_0 - \beta_1 x_i\big)^2$$

Squared, not absolute, for two reasons: it's differentiable everywhere (absolute value has a kink
at zero), and it punishes a single large miss more than several small ones of the same total size
— which is usually what you want in engineering, where one badly-underpredicted flood is worse
than several slightly-off ones. Set both partial derivatives to zero:

$$\frac{\partial \,\mathrm{SSE}}{\partial \beta_0} = -2\sum(y_i-\beta_0-\beta_1 x_i) = 0
\qquad\Rightarrow\qquad \hat\beta_0 = \bar y - \hat\beta_1 \bar x$$

$$\frac{\partial \,\mathrm{SSE}}{\partial \beta_1} = -2\sum x_i(y_i-\beta_0-\beta_1 x_i) = 0
\qquad\Rightarrow\qquad \hat\beta_1 = \frac{S_{xy}}{S_{xx}}$$

That's the whole derivation — two equations, two unknowns, both linear once you substitute the
first into the second. Two things worth carrying forward:

1. **$\hat\beta_1 = S_{xy}/S_{xx}$, and $r = S_{xy}/\sqrt{S_{xx}S_{yy}}$.** Standardize both
   variables (divide by their own standard deviations) and the slope *becomes* r. Correlation and
   regression are the same relationship, measured in two different units.
2. **This is a specific optimization, not a law of nature.** "Least squares" is a *choice* — least
   absolute deviations, or a weighted version that penalizes large-flood errors less (since their
   absolute errors are naturally larger), are equally legitimate choices with different answers.
   OLS is the default because it's the one with the closed-form solution above, not because it's
   uniquely correct.

### 2.3 Worked example — same six events

Reusing $S_{xy}=34{,}400$ and $S_{xx}=107{,}750$ from Section 1.3:

$$\hat\beta_1 = \frac{34{,}400}{107{,}750} = 0.3193 \text{ Mm}^3 \text{ per m}^3\text{/s}$$

$$\hat\beta_0 = 230.0 - (0.3193)(565.0) = 230.0 - 180.4 = 49.6 \text{ Mm}^3$$

$$\boxed{\hat V = 49.6 + 0.3193\,Q}$$

Predicted volume for a new 800 m³/s peak: $\hat V = 49.6 + 0.3193(800) = 305.0$ Mm³. (Read the
intercept as an artefact of fitting a line through this Q-range, not as "a zero-discharge flood
has 49.6 Mm³ of volume" — extrapolating a linear fit to x = 0 when the data lives between 380 and
750 is exactly the kind of overreach Section 1.4 warns about.)

**Residuals** — actual minus fitted, the vertical gaps the line didn't explain:

| Event | Q | V (actual) | $\hat V$ (fitted) | Residual | Residual² |
|---|---|---|---|---|---|
| 1 | 420 | 190 | 183.71 | +6.29 | 39.6 |
| 2 | 610 | 230 | 244.37 | −14.37 | 206.4 |
| 3 | 380 | 150 | 170.94 | −20.94 | 438.4 |
| 4 | 750 | 260 | 289.06 | −29.06 | 844.6 |
| 5 | 540 | 250 | 222.02 | +27.98 | 783.0 |
| 6 | 690 | 300 | 269.91 | +30.09 | 905.6 |
| | | | | **SSE** | **3217.5** |

### 2.4 R² and residuals

$$R^2 = 1 - \frac{\mathrm{SSE}}{S_{yy}} = 1 - \frac{3217.5}{14{,}200} = 0.7734$$

Cross-check: for simple linear regression, $R^2 = r^2$ exactly. Carrying r to more decimals than
Section 1.3 displayed, $r=0.87944$, and $0.87944^2 = 0.7734$. ✓ Same fact,
third outfit: 77% of the *variance* in flood volume across these six events is accounted for by a
straight-line relationship with peak discharge; the other 23% is everything else — antecedent
soil moisture, storm duration, catchment routing, measurement error.

Four assumptions make the *inference* from this fit trustworthy (not the point estimate itself,
which needs none of them): linearity, independent errors, constant error variance
(homoscedasticity), and — for confidence intervals specifically — normally distributed errors.
The one most likely to fail on real flood data is homoscedasticity: bigger floods usually come
with *bigger absolute* prediction errors (look at the residual column above — the two largest |Q|
points also have the two largest |residual|s), which is a standard motivation for fitting in log
space or weighting the regression. Worth checking before trusting a confidence interval on
$\hat\beta_1$, not before trusting $\hat\beta_1$ itself.

---

## 3. Rank correlation — Kendall's τ and Spearman's ρ

### 3.1 Why Pearson isn't always the right tool

Pearson r asks one specific question: *is the relationship close to a straight line?* It can
badly understate a relationship that is perfectly monotonic but curved. A **rank correlation**
asks a looser, more robust question instead: *as x increases, does y tend to increase (or
decrease) too — regardless of the shape?* **Kendall's τ** answers this by counting pairs.

Take every pair of events $(i,j)$. Call the pair **concordant** if the ranking agrees — the event
with the larger Q also has the larger V — and **discordant** if it disagrees.

$$\tau = \frac{C - D}{\tfrac{1}{2}n(n-1)}$$

$C$ = concordant pairs, $D$ = discordant pairs, and the denominator is just the total number of
pairs. $\tau=1$ means every single pair agrees on direction (a perfectly monotonic relationship,
however curved); $\tau=-1$ means every pair disagrees; $\tau=0$ means no consistent tendency.

### 3.2 Worked example — τ on the same six events

$n=6$ gives $\binom{6}{2}=15$ pairs. Going through all of them (event numbers, not sorted):

| Pair | Q's | V's | Agree? |
|---|---|---|---|
| 1–2 | 420, 610 | 190, 230 | C |
| 1–3 | 420, 380 | 190, 150 | C |
| 1–4 | 420, 750 | 190, 260 | C |
| 1–5 | 420, 540 | 190, 250 | C |
| 1–6 | 420, 690 | 190, 300 | C |
| 2–3 | 610, 380 | 230, 150 | C |
| 2–4 | 610, 750 | 230, 260 | C |
| **2–5** | 610, 540 | 230, 250 | **D** — smaller Q, larger V |
| 2–6 | 610, 690 | 230, 300 | C |
| 3–4 | 380, 750 | 150, 260 | C |
| 3–5 | 380, 540 | 150, 250 | C |
| 3–6 | 380, 690 | 150, 300 | C |
| 4–5 | 750, 540 | 260, 250 | C |
| **4–6** | 750, 690 | 260, 300 | **D** — smaller Q, larger V |
| 5–6 | 540, 690 | 250, 300 | C |

$C = 13$, $D = 2$, no ties.

$$\tau = \frac{13-2}{15} = \frac{11}{15} = \mathbf{0.733}$$

Compare to $r = 0.879$ on the *same* six points. Different questions, different numbers — and
that gap is not noise, it's information: it's telling you the relationship is a bit less
"straight-line" than r alone would suggest, even though it's still strongly monotonic. Both
discordant pairs involve event 5, the same point flagged in Section 1.3 for having a negative
cross-product — the two measures are picking up on the same real feature of the data from two
different angles.

### 3.3 The property that actually matters here: invariance

Apply a monotonic transform to Q — say $\log Q$, or $Q^3$ — and recompute both statistics on the
same six events:

| Transform of Q | r(·, V) | τ(·, V) |
|---|---|---|
| Q (untouched) | 0.879 | **0.733** |
| $\log Q$ | 0.902 | **0.733** |
| $Q^3$ | 0.816 | **0.733** |

r moves every time. τ **does not move at all** — verified numerically, not asserted. This is not
a coincidence: swapping every value for its rank throws away everything about the transform
*except* whether it preserved ordering, and a monotonic transform by definition preserves
ordering. τ depends only on ranks, so it cannot see the transform.

### 3.4 Spearman's ρ, briefly

**Spearman's ρ** is the other common rank correlation: convert both variables to ranks, then
compute ordinary Pearson r *on the ranks*. On this dataset, $\rho = 0.886$ — also invariant to
monotonic transforms, for the same reason as τ, but it weights disagreements differently (by
squared rank distance rather than by a plain concordant/discordant count) and doesn't have as
clean a link to a copula parameter. τ is the one this project actually uses.

| | Pearson r | Spearman ρ | Kendall τ |
|---|---|---|---|
| Measures | Linear association | Monotonic association (rank distance) | Monotonic association (pair concordance) |
| Range | [−1, 1] | [−1, 1] | [−1, 1] |
| Invariant to monotone transform of a margin? | No | Yes | Yes |
| Sensitive to outliers | Most | Less | Least |
| Closed-form link to a copula parameter | No | Approximate, family-dependent | Yes, several families (Section 4.2) |

---

## 4. Bridge to the CCH project

### 4.1 Why this project doesn't fit a copula with Pearson r

Sklar's theorem (Stats Day 2) splits a joint distribution into margins and a copula, and the two
can be chosen independently. The copula is supposed to be a statement about *dependence alone* —
but Pearson r is contaminated by the margins' shapes, as Section 3.3 just demonstrated directly:
the same underlying dependence gave three different r values depending on whether Q was measured
raw, logged, or cubed. Fit "the correlation" with Pearson r and you're partly describing the
choice of units, not the dependence. τ (or ρ) is invariant to exactly that choice, which is why it
survives the transform to uniform margins $U = F(X)$ untouched — it's measuring the copula, not
the margins wrapped around it.

### 4.2 Straight to Next Actions 2–3

Project Status's next concrete steps: compute $\hat\tau$ via `scipy.stats.kendalltau`, then
estimate the Gumbel copula parameter by method of moments, $\hat\theta = 1/(1-\hat\tau)$. The
worked τ from Section 3.2 makes this a two-line arithmetic step instead of an abstract formula:

$$\hat\theta_{\text{Gumbel}} = \frac{1}{1-\hat\tau} = \frac{1}{1 - 11/15} = \frac{1}{4/15}
= \frac{15}{4} = \mathbf{3.75}$$

For comparison, the Stats Day 2 interactive page fixed $\tau = 0.5$ throughout its examples,
giving $\theta = 1/(1-0.5) = 2$. This toy dataset's stronger dependence ($\tau=0.733$) gives a
noticeably higher $\theta = 3.75$ — a stronger Gumbel copula means more upper-tail dependence,
i.e. large peaks and large volumes are more likely to show up *together* than a weaker-θ family
would suggest. That's the whole point of fitting θ from data rather than assuming a value.

Two things this toy example is *not*: it's six illustrative points, not the real Nepal
peak/volume series (Project Status's outstanding blocker — "need real flood peak-volume
dataset" — is unrelated to this exercise and still open), and MOM is the fast first estimate, not
the final one. Next Action 3 also calls for cross-checking against pseudo-ML on the same
pseudo-observations, precisely because a large gap between the two would flag family
misspecification rather than an optimizer problem.

### 4.3 Where regression still earns its keep in this project

Copula fitting replaces "regress V on Q" as the tool for describing *dependence*, but ordinary
regression doesn't disappear from the workflow — it shows up in different places:

- **Regional frequency analysis** (a natural next step after the Day 3 finding that no single
  national ξ fits all five stations) often regresses GEV index-flood or shape parameters against
  catchment attributes (area, elevation, mean annual precipitation) to pool information across
  ungauged or short-record sites — literal OLS, just on different variables than Q and V.
  Homoscedasticity (Section 2.4) is worth checking there too: catchment attributes often relate
  to flood statistics multiplicatively, which is a log-regression signature.
- **Trend and covariate checks** on a fitted margin's parameters against time or an index like
  ENSO are a regression question, not a copula question.

### 4.4 What correlation still can't protect you from

τ = 0.733 is an *average* statement about the whole scatter, the same caveat Section 1.4 raised
for r. It says nothing on its own about what happens in the extreme corner — whether the two
biggest floods on record tend to coincide. That's a separate question, upper-tail dependence
$\lambda_U$, covered in the Stats Day 2 notes and interactive (panels 5–6): a Gumbel and a
Gaussian copula can be fitted to the *same* τ and give completely different answers about joint
extremes. Getting τ right is necessary for choosing among candidate copula families; it is not
sufficient for trusting any one family's tail behaviour — that check comes after, not instead of.

---

## 5. Cheat sheet

| Quantity | Formula | Says |
|---|---|---|
| Covariance sum | $S_{xy}=\sum(x_i-\bar x)(y_i-\bar y)$ | Do x and y move together, on average? |
| Pearson r | $S_{xy}/\sqrt{S_{xx}S_{yy}}$ | Strength + direction of the *linear* trend, in $[-1,1]$ |
| OLS slope | $\hat\beta_1 = S_{xy}/S_{xx}$ | Predicted unit change in y per unit change in x |
| OLS intercept | $\hat\beta_0 = \bar y - \hat\beta_1\bar x$ | Line's value at x = 0 (often not physically meaningful) |
| R² | $1 - \mathrm{SSE}/S_{yy}$, $=r^2$ for simple regression | Share of y's variance the line explains |
| Kendall's τ | $(C-D)/\binom{n}{2}$ | Probability a random pair agrees on direction, rescaled to $[-1,1]$ |
| Gumbel θ (MOM) | $1/(1-\hat\tau)$ | Copula parameter — how strong the upper-tail dependence is |

---

## 6. Practice problems

Try each before opening the solution. Problems 1–3 share the same summary statistics; problems
4–10 are independent.

**P1.** A dataset (not the flood one) has $n=10$, $\bar x=20$, $\bar y=15$, $S_{xx}=800$,
$S_{yy}=200$, $S_{xy}=350$. Compute r, the OLS slope, and the intercept.

<details markdown="1">
<summary>Solution</summary>

$r = 350/\sqrt{800 \times 200} = 350/400 = 0.875$

$\hat\beta_1 = 350/800 = 0.4375$

$\hat\beta_0 = 15 - 0.4375(20) = 15 - 8.75 = 6.25$
</details>

**P2.** Using the fitted line from P1, predict y at x = 30. Is this interpolation or
extrapolation, given $\bar x = 20$ and $S_{xx}=800$ (so x ranges roughly 20 ± a few multiples of
$\sqrt{800/10}\approx 8.9$)?

<details markdown="1">
<summary>Solution</summary>

$\hat y = 6.25 + 0.4375(30) = 6.25 + 13.125 = 19.375$.

x = 30 is about $(30-20)/8.9 \approx 1.1$ standard deviations above the mean — plausibly still
inside the data, so this is interpolation, not the kind of reckless extrapolation Section 2.3
warned about. (You'd need the actual x-range to be sure; SD alone is a rough guide.)
</details>

**P3.** If instead you were only told $R^2 = 0.81$ for this same dataset, what are the possible
values of r? Why can't you recover the sign from R² alone?

<details markdown="1">
<summary>Solution</summary>

$r = \pm\sqrt{0.81} = \pm 0.9$. R² is $r$ squared, and squaring destroys sign information — you'd
need to look at the scatter (or be told the slope's sign) to know which. This is exactly why
reporting R² alone in a results section, without the sign of the relationship, is incomplete.
</details>

**P4.** Compute Kendall's τ by hand for $x=(1,2,3,4)$, $y=(3,2,5,4)$.

<details markdown="1">
<summary>Solution</summary>

$\binom{4}{2}=6$ pairs:

| Pair | x's | y's | Agree? |
|---|---|---|---|
| 1–2 | 1,2 | 3,2 | D |
| 1–3 | 1,3 | 3,5 | C |
| 1–4 | 1,4 | 3,4 | C |
| 2–3 | 2,3 | 2,5 | C |
| 2–4 | 2,4 | 2,4 | C |
| 3–4 | 3,4 | 5,4 | D |

$C=4$, $D=2$. $\tau = (4-2)/6 = 0.333$.
</details>

**P5.** Stats Day 2's interactive fixed $\tau=0.5$ throughout its examples. What Gumbel θ does
that imply, and how does it compare to this document's worked θ = 3.75?

<details markdown="1">
<summary>Solution</summary>

$\theta = 1/(1-0.5) = 2$. Lower than this document's 3.75, because $\tau=0.5$ is weaker dependence
than $\tau=0.733$ — a smaller θ means less upper-tail dependence: extreme peaks and extreme
volumes co-occur less reliably under Day 2's assumed strength than under this document's worked
example.
</details>

**P6.** In your own words (no formula), explain why the project fits Kendall's τ instead of
Pearson's r before estimating a copula parameter. (Feynman-style — no numeric answer; the test is
whether you can say it without notation.)

<details markdown="1">
<summary>One acceptable answer</summary>

A copula is supposed to describe dependence alone, separately from whatever units or shape the
margins happen to have. Pearson r changes if you re-express one variable on a different scale
(log discharge instead of discharge, say) even though the actual dependence between the two
variables hasn't changed at all — so r is partly measuring the choice of units, not the
dependence. Kendall's τ only looks at which of two events had the bigger value on each variable,
never at *how much* bigger, so relabelling the scale can't change it. That makes τ a statement
about the copula and nothing else, which is the only kind of number Sklar's decomposition can
consistently ask for.
</details>

**P7.** True or false, and why: "r = 0.879 between peak and volume proves that a larger peak
*causes* a larger volume."

<details markdown="1">
<summary>Solution</summary>

False. r is symmetric and blind to mechanism — it's equally consistent with peak causing volume,
volume causing peak, or (most plausibly here) both being driven by a common cause, storm size and
duration. See interactive panel 6 for three worked examples of exactly this trap.
</details>

**P8.** Predict, before checking: if you cubed the *volume* values instead of the discharge
values in this document's six-event dataset, would τ(Q, V³) equal τ(Q, V)? Would r?

<details markdown="1">
<summary>Solution</summary>

τ would still be unchanged — cubing is a monotonic transform of *either* margin, and τ is
invariant to a monotonic transform of either one (Section 3.3 only demonstrated it on Q, but the
property holds symmetrically). r would change, for the same reason it changed under transforms of
Q.
</details>

**P9.** Using the residual table in Section 2.3, which single event contributes the most to SSE,
and does that match the event flagged in Sections 1.3 and 3.2 as breaking the "clean" pattern?

<details markdown="1">
<summary>Solution</summary>

Event 6 has the largest squared residual (905.6), narrowly ahead of event 4 (844.6) — not event 5,
which was the one flagged earlier. This is worth sitting with: the point with the "wrong-signed"
cross-product for r (event 5) and the discordant pairs for τ (events 5 and 4) is not the same
point as the worst-fitted point for the *regression line*. r, τ, and residual size are three
different lenses on the same six points, and they don't all light up the same point — which is
itself the lesson of Section 1.4 and Anscombe (panel 5): no single summary statistic tells the
whole story on its own.
</details>

**P10.** Fill in the blanks: r ranges from ___ to ___; the OLS slope equals $S_{xy}$ divided by
___; for simple linear regression, R² equals ___; the Gumbel copula's MOM parameter equals
1 divided by (1 minus ___).

<details markdown="1">
<summary>Solution</summary>

−1 to 1; $S_{xx}$; $r^2$; $\hat\tau$.
</details>

---

## 7. Feynman check

Correlation is one number that answers "when one of these goes up, does the other tend to go up
(or down) too, and how reliably?" Regression takes that same relationship and turns it into a
prediction machine: a line, fit by making the total squared prediction error as small as
possible. Both of them can be fooled — by a curve that isn't a line, by one weird point, by two
things that are both driven by some third thing neither of us has measured. Kendall's τ is a
sturdier version of the same idea: instead of asking "how well does a straight line fit," it just
asks "when I pick two floods at random, does the bigger-peak one also tend to be the bigger-volume
one" — a question that doesn't care whether you measured discharge in m³/s or its logarithm. That
sturdiness is exactly why the copula-fitting step in this project reaches for τ and not r: a
copula is only supposed to describe the *dependence*, and τ can't accidentally pick up the
units by mistake the way r can.

## 8. Where this leaves you

This document computed τ = 0.733 on six *illustrative* points, not the real Nepal series — the
"need real flood peak-volume dataset" blocker in Project Status is untouched by anything here.
What it should leave you with is confidence that Next Action 2
(`scipy.stats.kendalltau` on real pseudo-observations) and Next Action 3 (MOM θ̂, cross-checked
against pseudo-ML) are now two lines of arithmetic you've already done once by hand, not an
unfamiliar formula to look up cold.
