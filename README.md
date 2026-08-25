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
├── simulated-experiment/                      Stage 5: does CN exposure weaken the narrative
│   ├── main_simulated_experiment.ipynb        The experiment
│   ├── vanilla_cn_agent.py                    Vanilla generator, the unrefined baseline
│   ├── refined_pro_ukrainian_agents.py        Refined generators, the treatment
│   ├── pro_russian_agents_simulated_exp.py    Type 1 and Type 2 evaluator agents
│   └── simulated_experiment_results/          Evaluator scores for all three conditions
│
└── field-experiment/                          The online part: deployment on X
    ├── data/                                  The experiment data
    ├── notebooks/                             The analyses
    ├── figures/                               Finalized figures
    ├── outputs/                               Each notebook's own generated output
    └── n8n-workflows/                         The automation that ran the experiment
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

## The field experiment

The offline part establishes that the refined generators produce CNs that human
judges prefer and that reduce a narrative's appeal to a simulated pro-Russian
reader. The field experiment asks whether any of that survives deployment. The
sixty generators were run against live pro-Russian tweets on X, the resulting
CNs were posted as replies, and the tweets they answered were tracked for
fourteen days.

The headline result is that the replies increased the reach of the tweets they
answered rather than reducing it. Treated tweets gained more views than
untreated ones, 150 percent against 125 percent for the typical tweet, and those
extra views did not convert into likes or shares. The effect is close to uniform
across the tweet, the poster, the narrative and the objective the CN was
optimized for, which points at a platform distribution mechanic, a reply being
an engagement signal, rather than at anything about what the reply said.

### `data/`

| File | What it is |
|---|---|
| `Control_Group.xlsx` | 618 control tweets: text, URL, narrative, type, and 14-day engagement |
| `Treatment_Group.xlsx` | 592 treated tweets: the same, plus the CNs posted, the objective each was optimized for, and how many were posted |
| `Tweet Monitoring.xlsx` | the daily panel, views, likes, comments and shares per tweet across the fourteen days |
| `Existing_Users.xlsx` | poster account metadata: followers, following, bio, location, avatar, account age |
| `tweet_features.csv` | a derived per-tweet table used by three notebooks, produced by an upstream feature-build step that is not part of this repository |

### `notebooks/`

| Notebook | What it answers |
|---|---|
| `main_effect.ipynb` | Did the reply change how far the tweet spread, and does that depend on tweet type, narrative, detection lag or the CN's objective |
| `individual_effects.ipynb` | How many tweets were helped and how many hurt, one by one, and whether that holds across tweet sizes |
| `median_vs_mean.ipynb` | Whether the result is about the typical tweet or a handful of outliers |
| `trajectory_shape.ipynb` | When over the fourteen days the gap between the groups appears |
| `engagement_quality.ipynb` | Whether the extra views converted into likes |
| `engagement_rate_power.ipynb` | Whether a drop in likes or shares per view was detectable at all |
| `power_analysis.ipynb` | Whether the null results are real or the sample was too small |
| `poster_features_build.ipynb` | Build step: assembles the poster-account features. Calls paid APIs |
| `poster_features_analysis.ipynb` | Whether the effect depends on who posted, by reach and verification |

`figures/` holds the finalized figures. `outputs/` holds each notebook's own raw
output, which includes intermediate CSVs and earlier variants of some figures.

### `n8n-workflows/`

The two [n8n](https://n8n.io) workflows that operated the experiment, as
importable JSON. `Field Experiment - Main.json` is the main pipeline: it pulls
newly detected tweets, assigns each to Control or Treatment, generates the CN,
sends each batch for posting, and logs everything. `Monitoring Target Tweets.json`
is the recurring job that collects daily engagement across the fourteen-day
window.

**All credentials were removed before publication.** API keys, spreadsheet ids,
recipient addresses and n8n instance and webhook ids are placeholders. Supply
your own to run them.

---

## Running the code

Copy `.env.example` to `.env` and fill in the keys you need. Nothing is
hard-coded and `.env` is gitignored.

| Stage | Model | Key |
|---|---|---|
| Pilot generation | LLAMA-3.1-70B via Groq | `GROQ_API_KEY` |
| Refinement, human validation | Claude-3.5-Haiku via smolagents | `ANTHROPIC_API_KEY` |
| Simulated experiment, safety | Gemini 2.5 Flash | `GEMINI_API_KEY` |
| Field experiment, poster features | Gemini 2.5 Flash and XPOZ | `GEMINI_API_KEY`, `XPOZ_API_KEY` |

Python dependencies are in `requirements.txt`. The pilot's statistical analysis
is in R and uses `tidyverse`, `lme4`, `glmnet`, `performance`, `broom.mixed`,
`knitr` and `kableExtra`.

Notebooks resolve paths relative to their own directory, so run each one with
its folder as the working directory. Two exceptions, both of which work from
anywhere: `simulated-experiment/refined_pro_ukrainian_agents.py` and
`refinement-per-claim/safety_metrics/generate_cns.py` resolve against the
repository root.

The field experiment notebooks find their own root by walking up from the
working directory until they reach a folder containing `data`, so **run them
from `field-experiment/` or from `field-experiment/notebooks/`**, not from the
repository root. Started from the root they will stop at the top-level `Data/`
folder, which belongs to the offline part, and fail to find their inputs.

Only `poster_features_build.ipynb` calls paid APIs. Its output is committed, so
every analysis downstream of it runs without a key.

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

**Credentials and infrastructure identifiers for the field experiment.** The n8n
workflows are published with API keys, spreadsheet ids, recipient addresses and
instance and webhook ids replaced by placeholders.

**The upstream feature-build step for `tweet_features.csv`.** That table is
included, but the code that produced it sits outside this repository.

---

## Ethics

All aspects of this work were reviewed and approved by the Institutional Review
Boards of Tel Aviv University and Waseda University, the two institutions under
which it was jointly conducted.

The offline experiments were conducted in a controlled research environment. No
generated content was posted to any platform at that stage and no ordinary
social media user was exposed to a generated CN as part of them.

**The field experiment did post to a live platform.** Counter-narratives were
published as replies to real tweets and real users encountered them. Every
posting account stated in its bio that it was participating in academic
research. The tweets answered were public, and the replies were counter-speech
of a kind ordinary users post. No account was contacted privately, and no
attempt was made to influence any individual beyond the visible reply.

The human evaluators were informed that the task involved sensitive
Russia-Ukraine content and that the material they judged was generated by a
language model as part of a research study.

Data was collected from publicly available posts on X and public account
metadata. The accounts behind the evaluator agents appear in `Data/` because the
personas cannot be inspected or reproduced without them: an evaluator agent is
defined by the tweet history and summary that ground it, and withholding those
would leave the central instrument of the refinement process unauditable. The
field experiment data likewise identifies the authors of the tweets that were
answered, since the unit of analysis is the tweet and the analysis cannot be
checked without it.

Both are datasets about identifiable people who did not consent to being
studied. Anyone reusing them is asked to treat them accordingly, to consult X's
terms before redistributing, and in particular not to use the derived
account-level judgments in `field-experiment/outputs/poster_features/` to make
claims about any named individual. Those scores are model estimates produced for
aggregate analysis and are not evidence about any particular account.

Automated CNs carry risks of amplification and backlash. Any use outside a
research setting requires human oversight, safeguards and compliance with
platform policy.

---

## Licence

Code and released data are available under the [MIT License](LICENSE), with the
exception noted under *What is not included*: the CONAN and Multitarget-CONAN
derived files carry the terms of the original datasets.