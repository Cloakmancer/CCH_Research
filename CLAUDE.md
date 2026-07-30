# CCH Research Project

Civil engineer's graduate-research project on Compound Cascading Hazards (CCH), copula-based
hydrologic risk, SPH (DualSPHysics), and AI flood prediction. Primary domain: Nepal flood
hazards, GLOFs, hydropower risk. Full background: `Claude outputs/0.ContextTransfer.md`.

## Read these first, in order (short files — cheap to load)

1. `Claude outputs/1.ProjectStatud.md` — current phase, blockers, next actions. **Always check this before assuming what stage the project is at.**
2. `Claude outputs/2.ResearchLog.md` — dated log of what was done and decided.
3. `Claude outputs/0.ContextTransfer.md` — research vision, only if you need the big picture.

## Do NOT auto-load by default

`Claude outputs/3.KnowledgeBase.md.md` is a large (~40KB) reference doc (CCH typology, copula
theory, key equations, literature roadmap). Don't read it in full each session — `grep`/search
for the specific section needed (e.g. "AND vs OR", "Kendall", "Serinaldi"). Same for the PDFs
in that folder.

## Running a statistics study day

The user keeps a parallel elementary statistics track in `Stat_Study/` (separate folder, its own
`CLAUDE.md`). When they ask to "do the Day 1 treatment" for a new concept, follow
`tools/STUDY_DAY_PLAYBOOK.md` — six artefacts, the two wiring edits, house style and verification
steps, with Day 1 (2026-07-28) as the worked reference.

## Folder map

- `scripts/` — working Python scripts (Gumbel copula sampling, tail-dependence estimation,
  distribution references). Check filenames/dates before rewriting — may already exist.
- `data/`, `notebooks/`, `outputs/` — currently empty, awaiting real dataset.
- `Claude outputs/` — hand-off docs described above; also holds prior literature roadmap/
  workflow HTML files.

## Response style (user's stated preference)

Academic tone, critical evaluation, graduate-level depth. Do not oversimplify or pad with
beginner explanations for this project — that's reserved for the user's separate, genuinely
introductory statistics study (StatQuest playlist), which is scaffolding toward this project,
not the main event.

## Environment

Python via Miniconda: `E:\1.MINICONDA\python.exe` (not on system PATH — invoke by full path,
or use the user's activated conda env in VS Code). Key packages: numpy, scipy, pandas,
matplotlib, `pyvinecopulib`, PyTorch. GPU verified working (per project log).

## Keeping this system cheap on tokens

- Update `1.ProjectStatud.md` and append to `2.ResearchLog.md` at the end of a working
  session (or when asked) — a few lines, not a rewrite. This is the mechanism that replaces
  "re-explain everything next time."
- Prefer reading/updating these small status files over the large KnowledgeBase or PDFs.
- Don't duplicate content between this file and the `Claude outputs/` docs — this file only
  points to them.
