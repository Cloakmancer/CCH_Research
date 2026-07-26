# CCH Research Notes

Working notes for a graduate research project on **Compound Cascading Hazards** — copula-based
multivariate hydrologic risk, SPH free-surface modelling, and deep-learning flood prediction,
with Nepal flood hazards, GLOFs and hydropower risk as the application domain.

These are study and reference notes, not published results. They are made public because the
material is standard methodology; anything unpublished stays out of this repository.

---

## Start here

<div class="grid cards" markdown>

-   :material-book-open-variant: **[Revision: Copula · SPH · LSTM](revision-copula-sph-lstm.md)**

    Consolidated theory across all three methods, at working-competence depth. Each part opens
    with pre-questions to answer from memory and closes with a plain-language check.

-   :material-database: **[Knowledge Base](knowledge-base.md)**

    The long-form reference: CCH typology, copula theory, key equations, literature roadmap.

-   :material-map-marker-path: **[Literature Reading Guide](literature-guide.md)**

    What to read, in what order, and why.

-   :material-notebook: **[Research Log](research-log.md)**

    Dated record of what was done and decided.

</div>

---

## The three methods, and how they fit together

| | Copula | SPH | LSTM |
|---|---|---|---|
| Question | *How likely is this combination of drivers?* | *What does the flow physically do?* | *What will discharge be, given forcings?* |
| Type | Probabilistic | Deterministic / mechanistic | Data-driven |
| Strength | Correct joint tail behaviour | Violent free-surface flow, no meshing | Cheap, accurate, learns catchment memory |
| Weakness | No physics; tail estimated from few points | Cost; boundary treatment | No extrapolation; needs data |

The pipeline: a **copula** generates joint design scenarios on a return-period isoline; those
become boundary and initial conditions for **SPH** simulation of the resulting surge or breach;
the inundation and impact metrics are then combined with the scenario probabilities to give
*risk* rather than merely *hazard*. An **LSTM** enters either upstream — generating discharge
series where gauges are absent, so the copula has data to fit — or as an emulator of the
expensive SPH stage, making Monte Carlo over the full scenario space affordable.

---

## Searching

Use the search box at the top. It indexes the full text of every page, which is the practical
reason this exists as a site rather than a folder of files — the knowledge base alone is
~40 KB of prose.
