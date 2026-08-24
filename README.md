# Effective Counter-Narrative Generation Against Misinformation and Hate Speech: A Hybrid Human-AI Approach

Code and data accompanying the M.Sc. thesis of **Carmel Kronfeld**, School of
Industrial and Intelligent Systems Engineering, Tel Aviv University, supervised
by **Prof. Irad Ben-Gal**.

The thesis studies how to generate counter-narratives (CNs) against
misinformation and hate speech narratives, and whether CNs that are effective
under controlled evaluation remain effective once deployed on a live platform.
It has two parts. The **offline part** builds and validates a multi-stage,
agent-based pipeline for generating, refining and evaluating CNs against
pro-Russian narratives on the war in Ukraine. The **online part** deploys the
resulting generators on X and measures what happens to the posts they answer.

A paper presenting the offline part, *A Multi-Stage Agentic Framework for
Effective Counter-Narrative Generation and Refinement*, was accepted to the
International Natural Language Generation Conference (INLG 2026). This
repository is the thesis release and is broader than the one released with that
paper.

---

## Contents

```
.
├── Data/                                      Shared inputs, read by both stages below
│   ├── Pro Russian top users and narratives.xlsx   The 20 narratives, and the accounts
│   ├── pro_russian_users_data_for_agents.xlsx      The 18 evaluator personas
│   └── impersonation_validation_results_v2.csv     Persona fidelity results
│
├── pilot-experiment/                          Stage 1: which technique-style pairings work
│   ├── cn_generation_styles.ipynb             Generation of the pilot CNs
│   ├── cn_dataset_styles.csv                  Generated CNs, raw generation log
│   ├── cn_dataset_styles - Excel Version.xlsx Same CNs with the id columns used downstream
│   ├── comparisons_allocation.ipynb           Non-overlapping allocation of pairs to evaluators
│   ├── evaluations_russian_claims.csv         The human pairwise judgments
│   ├── pilot_statistical_model.html           Statistical analysis, knitted R Markdown
│   └── agreement_for_paper.ipynb              Evaluator consistency and inter-rater agreement
│
├── refinement-per-claim/                      Stage 2: per-narrative prompt refinement
│   ├── refinement_per_claim_final.ipynb       The refinement loop, orchestrates all agents
│   ├── pro_ukrainian_agents.py                CN Generator Agents, initial prompts
│   ├── pro_russian_agents_with_memory.py      Pro-Russian Evaluator Agents, with memory
│   ├── mediator_agent.py                      Mediator Agent
│   ├── manager_agent.py                       Manager Agent
│   ├── memory_summarizer_agent.py             Memory Summarizer Agent
│   ├── results_analysis_rpc.ipynb             Refinement curves, peaks, improvement deltas
│   ├── impersonation_validation.ipynb         Stage 2b: persona fidelity check
│   ├── refined_system_prompts/                The refined generator prompts, one file per narrative
│   ├── Refined_CN_Agents/                     The 60 refined generator agents as saved by the run
│   ├── refinement_per_claim_final_results/    Refinement logs, one folder per narrative
│   ├── group_analysis_results/                Figures, all six groups x three KPIs
│   ├── human-validation-initial/              Stage 3a: the diagnostic study,
│   │                                          incl. results_analysis.ipynb and
│   │                                          feedback.docx, the evaluators' comments
│   ├── human_validation-revised/              Stage 3b: the formal validation study,
│   │                                          incl. the post-revision prompts
│   └── safety_metrics/                        Stage 4: automated safety evaluation
│
└── simulated-experiment/                      Stage 5: does CN exposure weaken the narrative
    ├── main_simulated_experiment.ipynb        The experiment
    ├── vanilla_cn_agent.py                    Vanilla generator, the unrefined baseline
    ├── refined_pro_ukrainian_agents.py        Refined generators, the treatment
    ├── pro_russian_agents_simulated_exp.py    Type 1 and Type 2 evaluator agents
    └── simulated_experiment_results/          Evaluator scores for all three conditions
```

---

## The pilot experiment data

Three files describe the same 390 generated CNs and the judgments collected on
them. They are easiest to read together. The 390 are the full crossing the
thesis reports: 3 pro-Russian base claims x 13 rhetorical techniques x 10
writing styles, every cell generated once.

**`cn_dataset_styles.csv`** is the raw generation log written by
`cn_generation_styles.ipynb`: one row per generated CN, with the response id,
the CN text, the base claim it answers, the rhetorical technique, the writing
style, the model, and token counts.

**`cn_dataset_styles - Excel Version.xlsx`** is the same 390 CNs with the
integer id columns the rest of the pipeline joins on: `narrative_id` 1 to 390,
`base_claim_id` 1 to 3, `rhetorical_technique_id` 1 to 13 and `style_id` 1 to
10. It drops `response_id` and renames the CN text column to `narrative_text`.
This is the file `comparisons_allocation.ipynb` reads, and `narrative_id` is
the key that links a CN to the judgments collected on it.

**`evaluations_russian_claims.csv`** holds the human judgments: 7,650 rows,
which is 2,550 pairs each judged on three KPIs, 510 pairs per evaluator across
the five. Each row records the two CNs compared, the KPI, which side the
evaluator chose, and the response time. `kpi_id` is 1 persuasiveness,
2 emotional engagement, 3 shareability.

**`pilot_statistical_model.html`** is the knitted output of the statistical
analysis, run in R by Prof. Tetsuro Kobayashi. For each KPI it fits a
mixed-effects logistic regression of the pairwise choice with a random
intercept per evaluator and base claim, reports the intraclass correlation and
the fixed and random effects, and then fits a LASSO-regularized logistic
regression over the technique, style and technique-style interaction terms for
both sides of the comparison. The leading interaction per KPI is the result the
thesis reports and the configuration each generator agent is initialized with.

**`agreement_for_paper.ipynb`** covers evaluator reliability. Because the pairs
were allocated by non-overlapping random partition, no pair was seen by more
than one evaluator, which rules out the usual inter-rater statistics.
Reliability is therefore measured as internal consistency, a rank-biserial
correlation between each evaluator's choices and the ranking they imply, and as
ranking concordance, Kendall's *W* over per-evaluator Bradley-Terry fits, each
against a permutation baseline.

---

## The refinement data

**`Data/`** sits at the repository root because both the refinement stage and
the simulated experiment read from it. `Pro Russian top
users and narratives.xlsx` carries two sheets: the twenty narratives with their
descriptions, and the wider set of pro-Russian accounts from which the eighteen
behind the evaluator agents were drawn, with their activity and reach measures.
`pro_russian_users_data_for_agents.xlsx` holds, for each of those eighteen, the
tweet history and the language-model-generated summary of themes, tone and
stance that grounds the persona. `impersonation_validation_results_v2.csv` holds
the authorship attribution results, one row per held-out tweet, with the
agent's decision and its stated reasoning.

**`refined_system_prompts/`** holds the output of refinement: one Python file
per narrative, each defining the three refined generator prompts for that
narrative, one per KPI. `build_agents_prompts.py` collects all sixty into a
single table.

**`human_validation-revised/refined_system_prompts.xlsx`** is the same sixty
prompts *after* the naturalness and coherence guidelines were added following
the initial validation study. It is not a duplicate of the folder above: the
`.py` files are the prompts as the Manager produced them, and this workbook is
those prompts with the revision applied. The revised prompts are what the formal
validation study and the safety analysis use.

**`Refined_CN_Agents/`** is the agent tree the refinement run writes, one folder
per narrative and inside it one per generator: the serialized agent, its
configuration and its pickled memory. It is included so the refined generators
can be loaded directly rather than rebuilt from the prompts.

**`refinement_per_claim_final_results/`** holds the refinement logs, one folder
per narrative, with one CSV per generator. Each row is one iteration and records
the CN produced, the mean and standard deviation of each KPI across the eighteen
evaluators, the aggregated feedback the Mediator returned, and the system prompt
the Manager wrote in response. These are the files `results_analysis_rpc.ipynb`
reads to produce the refinement curves, the peak scores and the improvement
deltas.

---

## Running the code

Copy `.env.example` to `.env` and fill in the keys you need. Nothing is
hard-coded and `.env` is gitignored.

| Stage | Model | Key |
|---|---|---|
| Pilot generation | LLAMA-3.1-70B via Groq | `GROQ_API_KEY` |
| Refinement, human validation | Claude-3.5-Haiku via smolagents | `ANTHROPIC_API_KEY` |
| Simulated experiment, safety | Gemini 2.5 Flash | `GEMINI_API_KEY` |

Python dependencies are in `requirements.txt`. The pilot's statistical analysis
is in R and uses `tidyverse`, `lme4`, `glmnet`, `performance`, `broom.mixed`,
`knitr` and `kableExtra`.

Notebooks resolve paths relative to their own directory, so run each one with
its folder as the working directory. The two modules that reach across stages,
`simulated-experiment/refined_pro_ukrainian_agents.py` and
`refinement-per-claim/safety_metrics/generate_cns.py`, resolve against the
repository root instead and work from anywhere.

### Applying the refinement pipeline to another domain

The refinement pipeline is domain-agnostic. What changes between domains is the
input data; the architecture does not. You need three things.

**Target narratives.** A list of the harmful or misleading narratives to
counter. The thesis uses twenty pro-Russian narratives; one is enough to start.

**Evaluator personas.** One row per simulated audience member, with a username,
a 500 to 1,000 word summary of that persona's worldview, tone and stance,
sample texts representative of the persona, and contrasting texts from similar
but distinct personas so the agent can locate its own voice. The thesis uses
eighteen. Fewer but diverse personas can still drive meaningful refinement.

**Initial generator prompts.** Three generators are initialized, one per KPI,
in `pro_ukrainian_agents.py`. Adapt the stance and the assigned technique-style
pairing to your domain.

| What to change | Where |
|---|---|
| Target narratives | `claims` in `refinement_per_claim_final.ipynb` |
| Evaluator personas | the persona DataFrame in the same notebook |
| Generator stance and style | `pro_ukrainian_agents.py` |
| Backbone model | the model constructor in each agent file |
| Iteration limit, early-stop patience | `num_iterations`, `patience` in the notebook |
| KPI definitions and scoring | evaluator prompts in `pro_russian_agents_with_memory.py` |

The loop runs up to 25 iterations per narrative per KPI and stops early after 8
iterations without improvement. It keeps the prompt from the best-scoring
iteration, not the last.

---

## What is not included

**Agent run state other than the refined generators.** A refinement run also
writes the evaluator agents, the Manager and the Mediator to disk, along with
their accumulated memory. Those are large, are regenerated by any run, and add
nothing once the refined generators themselves are released, so they are left
out. `Refined_CN_Agents/` is the exception and is included in full.

**The mirror half of the pilot generation run.** The generation crossing was
originally run twice: once producing pro-Ukrainian CNs against pro-Russian base
claims, which is the pilot the thesis reports and which is released here, and
once producing pro-Russian CNs against pro-Ukrainian base claims. The second
half was never evaluated, never analysed and forms no part of the thesis, and
it is not released.

**Externally licensed corpora.** `safety_metrics/compute_metrics.py` downloads
CONAN and Multitarget-CONAN from their own repository at run time. The derived
score files here carry those datasets' terms, not this repository's licence.

---

## Ethics

All aspects of this work were reviewed and approved by the Institutional Review
Boards of Tel Aviv University and Waseda University, the two institutions under
which it was jointly conducted.

The offline experiments were conducted in a controlled research environment. No
generated content was posted to any platform at that stage and no ordinary
social media user was exposed to a generated CN as part of them.

The human evaluators were informed that the task involved sensitive
Russia-Ukraine content and that the material they judged was generated by a
language model as part of a research study.

Data was collected from publicly available posts on X. No private or personal
information was used, and no account was contacted, targeted or otherwise
affected by the offline work. The accounts behind the evaluator agents appear in
`refinement-per-claim/Data/` because the personas cannot be inspected or
reproduced without them: an evaluator agent is defined by the tweet history and
summary that ground it, and withholding those would leave the central
instrument of the refinement process unauditable. The material is limited to
public posts and public account-level metrics. Anyone reusing it is asked to
treat it as they would any dataset of identifiable people, and to consult X's
terms before redistributing it.

Automated CNs carry risks of amplification and backlash. Any use outside a
research setting requires human oversight, safeguards and compliance with
platform policy.

---

## Licence

Code and released data are available under the [MIT License](LICENSE), with the
exception noted under *What is not included*: the CONAN and Multitarget-CONAN
derived files carry the terms of the original datasets.