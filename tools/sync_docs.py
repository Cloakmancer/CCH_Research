#!/usr/bin/env python3
"""
Build the MkDocs `docs/` folder from the notes in `Claude outputs/`.

Why this exists: the note filenames contain spaces, leading digits and a double
extension (`3.KnowledgeBase.md.md`), none of which make good URLs. Rather than
rename the working files — which would break CLAUDE.md and the session workflow —
this script copies them into `docs/` under clean slugs at build time.

`docs/` is disposable and git-ignored. Edit the originals in `Claude outputs/`.

Usage:
    python tools/sync_docs.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Claude outputs"
DOCS = ROOT / "docs"
TOOLS = ROOT / "tools"

# source filename -> published slug.
# Files not listed here are NOT published. Add a line to publish something new.
MARKDOWN_MAP: dict[str, str] = {
    "0.ContextTransfer.md": "research-context.md",
    "2.ResearchLog.md": "research-log.md",
    "3.KnowledgeBase.md.md": "knowledge-base.md",
    "4.LiteratureReadingGuide.md": "literature-guide.md",
    "4.Revision_Copula_SPH_LSTM.md": "revision-copula-sph-lstm.md",
    "5.StatsStudyLog.md": "stats-study-log.md",
    "6.StatsProblemsDay1.md": "stats-problems-day1.md",
    "7.StatsProblemsDay2.md": "stats-problems-day2.md",
}

# Deliberately NOT published:
#   1.ProjectStatud.md   — working file, churns constantly, no value to a reader
#   *.pdf                — one is 22 MB; keep it out of git entirely

# Standalone interactive HTML pages, copied through as-is.
HTML_MAP: dict[str, str] = {
    "copula_families_interactive.html": "interactive/copula-families.html",
    "AND_OR_decision_framework.html": "interactive/and-or-decision.html",
    "Literature_Flowchart.html": "interactive/literature-flowchart.html",
    "CCH_literature_roadmap.html": "interactive/literature-roadmap.html",
    "CCH_study_workflow_plan.html": "interactive/study-workflow.html",
    "Skewness_and_Tails_interactive.html": "interactive/skewness-and-tails.html",
    "Probability_and_Copulas_interactive.html": "interactive/probability-and-copulas.html",
}


def clean_docs() -> None:
    # ignore_errors: some mounted/synced filesystems (OneDrive, network shares,
    # container bind mounts) refuse unlink on files they consider busy. A stale
    # leftover is harmless — every published file is rewritten below — whereas a
    # crash here would break the build.
    if DOCS.exists():
        shutil.rmtree(DOCS, ignore_errors=True)
    DOCS.mkdir(parents=True, exist_ok=True)


def _github_slug(text: str) -> str:
    """Reproduce GitHub's heading-anchor slug."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)  # drop punctuation, keep spaces
    s = re.sub(r"\s", "-", s)  # each space becomes its own hyphen
    return s


def _mkdocs_slug(text: str) -> str:
    """Reproduce Python-Markdown's toc slug (what MkDocs actually emits)."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[-\s]+", "-", s)  # runs of space/hyphen collapse to one
    return s.strip("-")


def rewrite_anchors(text: str) -> str:
    """
    Hand-written tables of contents in these notes use GitHub-style anchors.
    GitHub and MkDocs disagree whenever a heading contains punctuation that sits
    between spaces — an em dash in "Salvadori & De Michele (2004) — Copula
    Framework" gives GitHub `...2004--copula-framework` and MkDocs
    `...2004-copula-framework`. Left alone, every such TOC link 404s on the site.

    Build the mapping from the file's own headings and rewrite only links whose
    target is a GitHub slug that differs from the MkDocs one. Anything else is
    left untouched.
    """
    mapping: dict[str, str] = {}
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        if not m:
            continue
        heading = m.group(1)
        gh, md = _github_slug(heading), _mkdocs_slug(heading)
        if gh != md:
            mapping[gh] = md

    if not mapping:
        return text

    def repl(match: re.Match) -> str:
        target = match.group(1)
        return f"](#{mapping.get(target, target)})"

    return re.sub(r"\]\(#([^)]+)\)", repl, text)


def demote_headings(text: str) -> str:
    """
    MkDocs Material renders the first H1 as the page title. Notes that contain
    several H1s (the revision doc has one per part) end up with a confusing TOC.
    Keep the first H1, demote any later ones to H2 and shift their subtree down.
    """
    lines = text.split("\n")
    seen_h1 = False
    out: list[str] = []
    in_fence = False

    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        m = re.match(r"^(#{1,6})\s", line)
        if m:
            level = len(m.group(1))
            if level == 1:
                if not seen_h1:
                    seen_h1 = True
                else:
                    line = "#" + line  # H1 -> H2
        out.append(line)

    return "\n".join(out)


def sync_markdown() -> int:
    count = 0
    for src_name, dest_name in MARKDOWN_MAP.items():
        src = SRC / src_name
        if not src.exists():
            print(f"  ! missing, skipped: {src_name}", file=sys.stderr)
            continue
        text = src.read_text(encoding="utf-8")
        text = rewrite_anchors(text)
        text = demote_headings(text)
        dest = DOCS / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"  md   {src_name}  ->  {dest_name}")
        count += 1
    return count


def sync_html() -> list[str]:
    published: list[str] = []
    for src_name, dest_name in HTML_MAP.items():
        src = SRC / src_name
        if not src.exists():
            print(f"  ! missing, skipped: {src_name}", file=sys.stderr)
            continue
        dest = DOCS / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  html {src_name}  ->  {dest_name}")
        published.append(dest_name)
    return published


def write_interactive_index(published: list[str]) -> None:
    """Landing page linking the standalone HTML tools."""
    titles = {
        "interactive/copula-families.html": (
            "Copula Families",
            "Side-by-side comparison of Gumbel, Clayton, Frank and Gaussian "
            "dependence structures.",
        ),
        "interactive/and-or-decision.html": (
            "AND / OR Decision Framework",
            "Choosing the joint return period that matches the failure mechanism.",
        ),
        "interactive/literature-flowchart.html": (
            "Literature Flowchart",
            "Reading order and dependencies across the core papers.",
        ),
        "interactive/literature-roadmap.html": (
            "Literature Roadmap",
            "Thematic map of the CCH literature.",
        ),
        "interactive/study-workflow.html": (
            "Study Workflow Plan",
            "Phase plan from foundations through to the coupled workflow.",
        ),
        "interactive/skewness-and-tails.html": (
            "Why the Bell Curve Under-predicts Floods",
            "Five live panels on distribution shape: the two shapes, the return-period "
            "divergence, a simulated century of record, the rank transform, and the "
            "Gaussian-vs-Gumbel corner. Companion to the Statistics Study Log.",
        ),
        "interactive/probability-and-copulas.html": (
            "From a 2×2 Table to a Copula",
            "Six live panels taking marginal, joint and conditional probability from a "
            "contingency table through to upper-tail dependence and joint return "
            "periods: the Fréchet interval, the probability integral transform, "
            "Sklar's decomposition on separate controls, four families in the corner, "
            "and what independence costs a cascade. Companion to the Statistics "
            "Study Log.",
        ),
    }

    lines = [
        "# Interactive Pages",
        "",
        "Standalone HTML tools built earlier in the project. They open in a new tab.",
        "",
    ]
    for dest in published:
        title, desc = titles.get(dest, (Path(dest).stem, ""))
        lines.append(f"## [{title}]({dest}){{target=_blank}}")
        lines.append("")
        if desc:
            lines.append(desc)
            lines.append("")

    if not published:
        lines.append("*No interactive pages found.*")
        lines.append("")

    (DOCS / "interactive.md").write_text("\n".join(lines), encoding="utf-8")
    print("  gen  interactive.md")


def copy_assets() -> None:
    """Home page and static assets that live under tools/."""
    home = TOOLS / "home.md"
    if home.exists():
        shutil.copy2(home, DOCS / "index.md")
        print("  gen  index.md")

    assets = TOOLS / "assets"
    if assets.exists():
        shutil.copytree(assets, DOCS, dirs_exist_ok=True)
        print("  gen  assets")


def main() -> None:
    if not SRC.exists():
        sys.exit(f"Source folder not found: {SRC}")

    print(f"Syncing notes -> {DOCS}")
    clean_docs()
    n = sync_markdown()
    published = sync_html()
    write_interactive_index(published)
    copy_assets()
    print(f"Done. {n} markdown pages, {len(published)} interactive pages.")


if __name__ == "__main__":
    main()
