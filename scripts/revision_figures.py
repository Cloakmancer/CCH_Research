"""
Figures for `Claude outputs/4.Revision_Copula_SPH_LSTM.md`.

Writes PNGs into tools/assets/images/, which tools/sync_docs.py copies to
docs/images/ — so the published page references them as "images/<name>.png".

    E:\\1.MINICONDA\\python.exe scripts\\revision_figures.py

Deliberately depends on nothing beyond numpy/scipy/matplotlib: the copula
samplers and CDFs are written out below rather than pulled from
pyvinecopulib, so the figures regenerate in any environment. Where a family's
diagonal section C(u,u) has a closed form it is used directly instead of being
estimated from a sample — the whole point of the tail-dependence figure is
behaviour at u → 1, which is exactly where sampling error is worst.
"""

import os
from math import log, exp, sqrt

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
from scipy import stats, optimize, integrate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "assets", "images")
os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#1a1a19", "#52514e", "#e2e0d8"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": MUTED, "axes.edgecolor": GRID,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 150,
})

RNG = np.random.default_rng(20260728)
TAU = 0.5


def finish(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------------------------ copulas
def theta_gumbel(tau):  return 1 / (1 - tau)
def theta_clayton(tau): return 2 * tau / (1 - tau)


def theta_frank(tau):
    """Frank's tau has only a Debye-function form; invert it numerically."""
    def debye1(t):
        return integrate.quad(lambda x: x / (np.exp(x) - 1), 0, t)[0] / t

    def f(th):
        return 1 - 4 / th * (1 - debye1(th)) - tau

    return optimize.brentq(f, 1e-6, 60)


def sample_gaussian(n, rho):
    z = RNG.multivariate_normal([0, 0], [[1, rho], [rho, 1]], size=n)
    return stats.norm.cdf(z)


def sample_t(n, rho, nu=4):
    z = RNG.multivariate_normal([0, 0], [[1, rho], [rho, 1]], size=n)
    w = RNG.chisquare(nu, size=n)
    t = z / np.sqrt(w / nu)[:, None]
    return stats.t.cdf(t, nu)


def sample_gumbel(n, th):
    """Marshall-Olkin with a positive-stable frailty (Chambers-Mallows-Stuck)."""
    a = 1 / th
    u = np.pi * RNG.random(n)
    w = RNG.exponential(size=n)
    s = (np.sin(a * u) / np.sin(u) ** (1 / a) *
         (np.sin((1 - a) * u) / w) ** ((1 - a) / a))
    e = RNG.exponential(size=(n, 2))
    return np.exp(-(e / s[:, None]) ** a)


def sample_clayton(n, th):
    """Marshall-Olkin with a Gamma(1/theta) frailty."""
    s = RNG.gamma(1 / th, 1.0, size=n)
    e = RNG.exponential(size=(n, 2))
    return (1 + e / s[:, None]) ** (-1 / th)


def sample_frank(n, th):
    """Conditional inversion — closed form for Frank."""
    u = RNG.random(n)
    w = RNG.random(n)
    v = -1 / th * np.log(1 + w * (1 - np.exp(-th)) /
                         (w * (np.exp(-th * u) - 1) - np.exp(-th * u)))
    return np.column_stack([u, v])


# diagonal sections C(u,u) — closed form beats sampling in the far tail
def C_gumbel(u, th):  return u ** (2 ** (1 / th))
def C_clayton(u, th): return (2 * u ** (-th) - 1) ** (-1 / th)


def C_frank(u, th):
    return -1 / th * np.log(1 + (np.exp(-th * u) - 1) ** 2 / (np.exp(-th) - 1))


def C_gauss(u, rho):
    mvn = stats.multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
    z = stats.norm.ppf(u)
    return np.array([mvn.cdf([zi, zi]) for zi in np.atleast_1d(z)])


def C_t(u, rho, nu=4):
    mvt = stats.multivariate_t(loc=[0, 0], shape=[[1, rho], [rho, 1]], df=nu)
    z = stats.t.ppf(u, nu)
    return np.array([mvt.cdf([zi, zi]) for zi in np.atleast_1d(z)])


# =================================================== §1.2  Sklar's theorem
def fig_sklar():
    n = 1200
    th = theta_gumbel(TAU)
    uv = sample_gumbel(n, th)
    # real units: peak (lognormal) and volume (lognormal), different shapes
    peak = stats.lognorm.ppf(uv[:, 0], 0.51, scale=700)
    vol = stats.lognorm.ppf(uv[:, 1], 0.75, scale=260)

    fig = plt.figure(figsize=(11.2, 3.7))
    gs = fig.add_gridspec(1, 3, wspace=.32)

    ax = fig.add_subplot(gs[0])
    ax.scatter(peak, vol, s=9, color=BLUE, alpha=.35, edgecolor="none")
    ax.set_xlabel("flood peak (m³/s)")
    ax.set_ylabel("flood volume (Mm³)")
    ax.set_title("① What you observe\njoint distribution H(x,y)")
    ax.set_xlim(0, 2600)
    ax.set_ylim(0, 1400)

    # Two margins, two units — so two stacked axes rather than one shared scale.
    inner = gs[1].subgridspec(2, 1, hspace=.75)
    for k, (data, lo, hi, sig, sc, col, lab, unit) in enumerate((
            (peak, 0, 2600, 0.51, 700, BLUE, "peak margin  F", "m³/s"),
            (vol, 0, 1400, 0.75, 260, ORANGE, "volume margin  G", "Mm³"))):
        axm = fig.add_subplot(inner[k])
        xs = np.linspace(1, hi, 400)
        axm.hist(data, bins=34, density=True, color=col, alpha=.28, range=(lo, hi))
        axm.plot(xs, stats.lognorm.pdf(xs, sig, scale=sc), color=col, lw=2)
        axm.set_yticks([])
        axm.set_xlim(lo, hi)
        axm.set_xlabel(unit, labelpad=1, fontsize=9)
        axm.text(.97, .86, lab, transform=axm.transAxes, ha="right", fontsize=9.5,
                 color=col, weight="bold")
        axm.grid(False)
        if k == 0:
            axm.set_title("② Strip out the margins\neach variable's own shape")

    ax = fig.add_subplot(gs[2])
    ax.scatter(uv[:, 0], uv[:, 1], s=9, color=ORANGE, alpha=.38, edgecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("u = F(peak)")
    ax.set_ylabel("v = G(volume)")
    ax.set_title("③ What is left is the copula\nC(u,v) — pure dependence")

    fig.suptitle("Sklar:  H(x,y) = C(F(x), G(y))   — the copula is extracted, not imposed",
                 y=1.06, fontsize=12, fontweight="bold")
    finish(fig, "rev-sklar-decomposition.png")


# =================================================== §1.5  family shapes
def fig_families():
    n = 2500
    fams = [
        ("Gaussian", sample_gaussian(n, np.sin(np.pi * TAU / 2)), "λ_U = 0, λ_L = 0"),
        ("Student-t (ν=4)", sample_t(n, np.sin(np.pi * TAU / 2)), "λ_U = λ_L > 0"),
        ("Frank", sample_frank(n, theta_frank(TAU)), "λ_U = 0, λ_L = 0"),
        ("Gumbel", sample_gumbel(n, theta_gumbel(TAU)), "λ_U > 0, λ_L = 0"),
        ("Clayton", sample_clayton(n, theta_clayton(TAU)), "λ_U = 0, λ_L > 0"),
        ("Independence", RNG.random((n, 2)), "τ = 0"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(10.4, 7.0))
    for ax, (name, uv, note) in zip(axes.ravel(), fams):
        corner = (uv[:, 0] > .9) & (uv[:, 1] > .9)
        low = (uv[:, 0] < .1) & (uv[:, 1] < .1)
        ax.scatter(uv[~(corner | low), 0], uv[~(corner | low), 1], s=6,
                   color=BLUE, alpha=.28, edgecolor="none")
        ax.scatter(uv[corner, 0], uv[corner, 1], s=11, color=ORANGE, alpha=.9,
                   edgecolor="none")
        ax.scatter(uv[low, 0], uv[low, 1], s=11, color=ORANGE, alpha=.45, edgecolor="none")
        for lo in (0.9, 0.1):
            ax.axvline(lo, color=MUTED, lw=.8, ls=(0, (2, 3)))
            ax.axhline(lo, color=MUTED, lw=.8, ls=(0, (2, 3)))
        ax.set_title(f"{name}", fontsize=10.5)
        ax.text(.02, .965, note, transform=ax.transAxes, fontsize=8.5, color=MUTED,
                va="top")
        ax.text(.97, .03, f"{corner.sum()} in upper corner", transform=ax.transAxes,
                fontsize=8.5, color=ORANGE, ha="right", weight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([0, .5, 1])
        ax.set_yticks([0, .5, 1])
        ax.grid(False)
    fig.suptitle("Same Kendall's τ = 0.5 in all five dependent panels — the corners differ",
                 y=.985, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .96))
    finish(fig, "rev-copula-families.png")


# =================================================== §1.4  tail dependence
def fig_tail_dependence():
    u = np.linspace(0.50, 0.9995, 320)
    rho = np.sin(np.pi * TAU / 2)
    thG, thC, thF = theta_gumbel(TAU), theta_clayton(TAU), theta_frank(TAU)

    def lam(Cuu):
        return (1 - 2 * u + Cuu) / (1 - u)

    # scipy's multivariate_t.cdf is Monte-Carlo, so the t curve turns to noise as
    # u -> 1. Draw it only where it is trustworthy and join it to its ANALYTIC
    # limit, which is the value the figure is actually making a claim about.
    nu = 4
    lam_t = 2 * stats.t.cdf(-sqrt((nu + 1) * (1 - rho) / (1 + rho)), nu + 1)
    cut = u <= 0.99

    curves = [
        ("Gumbel",        u,         lam(C_gumbel(u, thG)),      ORANGE),
        ("Student-t ν=4", u[cut],    lam(C_t(u, rho))[cut],      MAGENTA),
        ("Gaussian",      u,         lam(C_gauss(u, rho)),       BLUE),
        ("Frank",         u,         lam(C_frank(u, thF)),       AQUA),
        ("Clayton",       u,         lam(C_clayton(u, thC)),     YELLOW),
    ]
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    ends = []
    for name, xs, y, col in curves:
        ax.plot(xs, y, color=col, lw=2.4)
        ends.append([y[-1], name, col])
    ax.plot([u[cut][-1], 1.0], [curves[1][2][-1], lam_t],
            color=MAGENTA, lw=2.4, ls=(0, (4, 3)))
    ax.scatter([1.0], [lam_t], s=34, color=MAGENTA, zorder=5, clip_on=False)
    ends[1][0] = lam_t

    # nudge end-labels apart: Frank and Clayton both land on zero
    ends.sort(key=lambda e: e[0])
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + .045)
    for y, name, col in ends:
        ax.annotate(f" {name}", xy=(1.0, y), xytext=(7, 0), textcoords="offset points",
                    color=col, fontsize=9.5, weight="bold", va="center",
                    annotation_clip=False)

    ax.axhline(2 - 2 ** (1 / thG), color=ORANGE, lw=1, ls=(0, (3, 3)))
    ax.text(0.505, 2 - 2 ** (1 / thG) + .018, "λ_U = 2 − 2^(1/θ) = 0.586", color=ORANGE,
            fontsize=9)
    ax.axvspan(0.9, 0.99, color=MUTED, alpha=.07)
    ax.text(0.945, 0.845, "the window you can\nactually diagnose\nwith 40 years",
            ha="center", fontsize=8.6, color=MUTED)
    ax.set_xlim(0.5, 1.0)
    ax.set_ylim(0, 1)
    ax.set_xlabel("u  —  “extreme” means above this quantile")
    ax.set_ylabel("P(V > u | U > u)")
    ax.set_title("Five families, identical τ = 0.5, opposite claims about the corner", loc="left")
    ax.set_axisbelow(True)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    fig.subplots_adjust(right=.84)
    finish(fig, "rev-tail-dependence.png")


# =================================================== §1.9  AND / OR isolines
def fig_and_or():
    th, T = theta_gumbel(TAU), 100.0
    Cg = lambda u, v: np.exp(-(((-np.log(u)) ** th + (-np.log(v)) ** th) ** (1 / th)))

    # OR: C(u,v) = 1 - 1/T  -> closed form for v
    t = 1 - 1 / T
    lu = np.linspace(-np.log(t) * 1e-6, (-np.log(t)) * (1 - 1e-9), 400)
    u_or = np.exp(-lu)
    v_or = np.exp(-(((-np.log(t)) ** th - lu ** th) ** (1 / th)))

    # AND: 1 - u - v + C(u,v) = 1/T  -> solve for v
    u_and = np.linspace(0.9, 0.99999, 260)
    v_and = []
    for ui in u_and:
        f = lambda v: 1 - ui - v + Cg(ui, v) - 1 / T
        try:
            v_and.append(optimize.brentq(f, 1e-9, 1 - 1e-12))
        except ValueError:
            v_and.append(np.nan)
    v_and = np.array(v_and)

    q = lambda u: stats.lognorm.ppf(u, 0.51, scale=700)      # peak, m³/s
    w = lambda u: stats.lognorm.ppf(u, 0.75, scale=260)      # volume, Mm³
    XLO, XHI, YLO, YHI = 1500, 4200, 400, 3000

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.plot(q(u_or), w(v_or), color=BLUE, lw=2.6, label="T$_{OR}$ = 100 yr  (either exceeds)")
    ax.plot(q(u_and), w(v_and), color=ORANGE, lw=2.6,
            label="T$_{AND}$ = 100 yr  (both exceed)")

    # every point on a curve is the same T — mark several to make that concrete
    for frac in (0.12, 0.4, 0.72):
        i = int(len(u_and) * frac)
        ax.scatter(q(u_and[i]), w(v_and[i]), s=46, color=ORANGE, zorder=5,
                   edgecolor=SURFACE, linewidth=1.5)
    i = int(len(u_and) * .4)
    ax.annotate("every point on a curve carries the\nsame return period — an isoline,\nnot a single design event",
                xy=(q(u_and[i]), w(v_and[i])), xytext=(1560, 1900), fontsize=9.5, color=ORANGE,
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))

    # the symmetric point on each curve, to anchor the comparison
    us = optimize.brentq(lambda z: 1 - 2 * z + Cg(z, z) - 1 / T, .9, 1 - 1e-12)
    ax.scatter([q(us)], [w(us)], s=70, color=ORANGE, zorder=6, edgecolor=SURFACE, linewidth=1.8)
    ax.annotate("at THIS point:  T$_{AND}$ = 100 yr  but  T$_{OR}$ = 42 yr\n"
                "— the same event, two answers, because they are\ntwo different questions about failure",
                xy=(q(us), w(us)), xytext=(1545, 560), fontsize=9.3, color=INK,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2))

    ax.annotate("AND is the rarer event, so for a FIXED T its isoline\n"
                "sits CLOSER IN — pick AND where the physics is OR\n"
                "and you design to a smaller event while quoting\n"
                "the same return period",
                xy=(3450, 1470), xytext=(2620, 700), fontsize=9.3, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_xlabel("flood peak (m³/s)")
    ax.set_ylabel("flood volume (Mm³)")
    ax.set_title("The same “100-year event”, two different questions", loc="left")
    ax.legend(loc="upper right")
    ax.set_axisbelow(True)
    finish(fig, "rev-and-or-isolines.png")


# =================================================== §2.2  SPH kernel
def fig_sph_kernel():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2),
                             gridspec_kw={"width_ratios": [1.15, 1]})
    rng = np.random.default_rng(3)
    pts = rng.uniform(-3, 3, size=(220, 2))
    a, h = np.array([0.0, 0.0]), 1.0
    d = np.linalg.norm(pts - a, axis=1)
    inside = d < 2 * h

    ax = axes[0]
    ax.scatter(pts[~inside, 0], pts[~inside, 1], s=26, color=MUTED, alpha=.30,
               edgecolor="none")
    ax.scatter(pts[inside, 0], pts[inside, 1], s=34, color=BLUE, alpha=.75,
               edgecolor="none")
    ax.scatter([0], [0], s=90, color=ORANGE, zorder=5, edgecolor=SURFACE, linewidth=1.6)
    for r, ls in ((h, (0, (4, 3))), (2 * h, "-")):
        ax.add_patch(Circle((0, 0), r, fill=False, ec=ORANGE, lw=1.4, ls=ls, alpha=.9))
    ax.annotate("h", xy=(h * .71, h * .71), xytext=(1.15, 1.25), color=ORANGE, fontsize=10,
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.1))
    ax.annotate("2h — support radius:\nonly these neighbours contribute",
                xy=(2 * h * .71, -2 * h * .71), xytext=(0.6, -2.75), color=ORANGE, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.1))
    ax.text(-2.9, 2.6, "particle a", color=ORANGE, fontsize=10, weight="bold")
    ax.set_aspect("equal")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title("No mesh — just neighbours inside 2h", loc="left")

    ax = axes[1]
    q = np.linspace(0, 2.4, 400)
    W = np.where(q <= 1, 1 - 1.5 * q ** 2 + 0.75 * q ** 3,
                 np.where(q <= 2, 0.25 * (2 - q) ** 3, 0)) * (10 / (7 * np.pi))
    ax.plot(q, W, color=BLUE, lw=2.6)
    ax.fill_between(q, W, color=BLUE, alpha=.13)
    ax.axvline(2, color=ORANGE, lw=1.4, ls=(0, (4, 3)))
    ax.text(2.02, max(W) * .55, " W = 0 beyond 2h\n (compact support)", color=ORANGE, fontsize=9)
    ax.set_xlabel("q = r / h")
    ax.set_ylabel("W(q)  —  kernel weight")
    ax.set_title("Cubic spline kernel: near neighbours count most", loc="left")
    ax.set_axisbelow(True)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)

    fig.suptitle(r"$A(\mathbf{r}_a)\approx\sum_b \frac{m_b}{\rho_b} A_b\, W(|\mathbf{r}_a-\mathbf{r}_b|, h)$"
                 "        — interpolate any field from the neighbours, weighted by W",
                 y=1.03, fontsize=11.5)
    fig.tight_layout()
    finish(fig, "rev-sph-kernel.png")


# =================================================== §3.2  vanishing gradient
def fig_vanishing_gradient():
    lag = np.arange(0, 366)
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    for sv, col, lab in ((1.2, MAGENTA, "‖W‖ = 1.2  → explodes"),
                         (0.98, BLUE, "‖W‖ = 0.98 → vanishes"),
                         (0.9, AQUA, "‖W‖ = 0.90 → vanishes fast")):
        ax.plot(lag, sv ** lag, color=col, lw=2.3, label=lab)
    ax.plot(lag, 0.999 ** lag, color=ORANGE, lw=2.8,
            label="LSTM cell path, forget gate ≈ 0.999")
    ax.axhline(1, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.set_yscale("log")
    ax.set_ylim(1e-18, 1e8)
    ax.set_xlim(0, 365)
    ax.axvspan(180, 365, color=MUTED, alpha=.07)
    ax.text(272, 1e5, "a season of catchment memory\n(snowpack, groundwater)",
            ha="center", fontsize=9, color=MUTED)
    ax.set_xlabel("time steps back through the sequence (days)")
    ax.set_ylabel("gradient magnitude reaching this lag (log scale)")
    ax.set_title("Why a plain RNN cannot learn seasonal memory — and what the cell state fixes",
                 loc="left")
    ax.legend(loc="lower left", fontsize=9.5)
    ax.set_axisbelow(True)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    finish(fig, "rev-vanishing-gradient.png")


# =================================================== §3.3  LSTM cell
def fig_lstm_cell():
    fig, ax = plt.subplots(figsize=(10.6, 4.9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.6)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch((1.4, .55), 9.2, 4.0,
                                boxstyle="round,pad=0.05,rounding_size=.18",
                                fc="#2a78d60a", ec=GRID, lw=1.4))

    # the additive highway
    ax.annotate("", xy=(11.0, 3.95), xytext=(1.0, 3.95),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=3.4, mutation_scale=18))
    ax.text(1.0, 4.32, "c$_{t-1}$", fontsize=11, color=ORANGE, weight="bold", ha="center")
    ax.text(11.0, 4.32, "c$_t$", fontsize=11, color=ORANGE, weight="bold", ha="center")
    ax.text(6.2, 4.62, "THE CELL STATE — an additive conveyor, not a repeated matrix multiply",
            fontsize=10, color=ORANGE, weight="bold", ha="center")

    XF, XI, XC, XO = 2.7, 4.9, 6.8, 9.4
    XPLUS, YMERGE = 6.0, 3.10

    for x, sym in ((XF, "×"), (XPLUS, "+")):
        ax.add_patch(Circle((x, 3.95), .30, fc=SURFACE, ec=ORANGE, lw=1.8, zorder=4))
        ax.text(x, 3.95, sym, ha="center", va="center", fontsize=13, color=ORANGE,
                zorder=5, weight="bold")
    # i_t and the candidate combine first, then enter the highway once
    ax.add_patch(Circle((XPLUS, YMERGE), .22, fc=SURFACE, ec=MUTED, lw=1.4, zorder=4))
    ax.text(XPLUS, YMERGE, "⊙", ha="center", va="center", fontsize=9, color=MUTED, zorder=5)
    ax.annotate("", xy=(XPLUS, 3.62), xytext=(XPLUS, YMERGE + .24),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.5, mutation_scale=12))

    gates = [(XF, "f$_t$", "forget\ncarry stored\nstate forward", BLUE, "highway"),
             (XI, "i$_t$", "input\nwrite new\nforcing in", BLUE, "merge"),
             (XC, "c̃$_t$", "candidate\nwhat the new\ninformation is", MUTED, "merge"),
             (XO, "o$_t$", "output\nexpose the\nstore now", BLUE, "none")]
    for x, sym, lab, col, route in gates:
        ax.add_patch(FancyBboxPatch((x - .46, 1.70), .92, .60,
                                    boxstyle="round,pad=0.03,rounding_size=.10",
                                    fc="#2a78d61f" if col == BLUE else "#f0efec",
                                    ec=col, lw=1.5, zorder=3))
        ax.text(x, 2.00, sym, ha="center", va="center", fontsize=11.5, color=col,
                weight="bold", zorder=4)
        ax.text(x, 1.54, lab, ha="center", va="top", fontsize=8.1, color=MUTED)
        if route == "highway":
            ax.annotate("", xy=(x, 3.62), xytext=(x, 2.36),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4, mutation_scale=11))
        elif route == "merge":
            ax.annotate("", xy=(XPLUS + (-.17 if x < XPLUS else .17), YMERGE - .16),
                        xytext=(x, 2.36),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4, mutation_scale=11,
                                        connectionstyle="angle3,angleA=90,angleB=30"))

    ax.text(.72, 2.74, "h$_{t-1}$, x$_t$", fontsize=10.5, color=INK, ha="center", weight="bold")
    ax.annotate("", xy=(9.9, 2.74), xytext=(1.35, 2.74),
                arrowprops=dict(arrowstyle="-", color=GRID, lw=1.6))
    for x, _, _, _, _ in gates:
        ax.plot([x], [2.74], marker="o", ms=4.5, color=GRID)
        ax.plot([x, x], [2.36, 2.74], color=GRID, lw=1.2)

    # h_t leaves sideways from the gate box — any vertical run would cross the
    # centred caption underneath it
    ax.annotate("", xy=(11.0, 2.00), xytext=(XO + .46, 2.00),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.2, mutation_scale=14))
    ax.text(11.05, 2.00, " h$_t$", fontsize=11, color=BLUE, weight="bold", va="center")
    ax.text(10.35, 2.34, "= o$_t$ ⊙ tanh(c$_t$)", fontsize=8.6, color=MUTED, ha="center")

    ax.text(5.4, .14,
            "gates are σ-valued soft switches in (0,1), learned and input-dependent — "
            "hydrologically: recession · infiltration · release",
            ha="center", fontsize=9, color=MUTED, style="italic")
    finish(fig, "rev-lstm-cell.png")


if __name__ == "__main__":
    print("writing figures to", OUT)
    fig_sklar()
    fig_families()
    fig_tail_dependence()
    fig_and_or()
    fig_sph_kernel()
    fig_vanishing_gradient()
    fig_lstm_cell()
    print("done")
