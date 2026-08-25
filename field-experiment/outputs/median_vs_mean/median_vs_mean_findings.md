# Averages-Based Re-Analysis: Findings

> Median-based results remain **primary** (robust to the heavy viral tail). Mean-based views are reported only where they are *substantively informative*. Two contrasts are informative; everything else is consistent-null across both views.

---

## Finding 1 — Views main effect: the median and the mean tell different stories (IMPORTANT)

| View | Treatment | Control | Diff (T−C) | p | Verdict |
|---|---|---|---|---|---|
| **Median (MWU)** — published headline | 150 | 125 | **+25** | **0.0002** | Treatment grows MORE (anti-suppression), significant |
| **Mean, raw** | 502 | **6,911** | **−6,409** | 0.30 (ns) | Control higher — but driven by tail, not significant |
| **Mean, winsorized (p99)** | 458 | 449 | +9 | 0.88 (ns) | Essentially tied |

**What's happening:** Control's *raw mean* (6,911% growth) is ~14× Treatment's (502%) — but this is the work of a tiny number of mega-viral Control tweets. Control's skew is **24.8** vs Treatment's 11.0. Clip the top 1% (winsorize) and the gap collapses to +9 (favoring Treatment again), non-significant.

**Interpretation:** The anti-suppression effect is a **typical-tweet (central-tendency) phenomenon** — the median tweet grows more views under Treatment, robustly. It is **not** a tail phenomenon: the handful of extreme viral events in our sample happened to land in Control, but (a) they're ~6 tweets, (b) the difference is not significant (p=0.30), and (c) means are notoriously unstable under engagement distributions this skewed.

**Why this matters for the paper:** A reviewer who computes mean total Views will see Control > Treatment and may challenge the anti-suppression claim. We now have the answer ready:
> *"CN replies increase the median tweet's view growth (MWU p=0.0002). The arithmetic mean is dominated by a small number of viral tweets (Control skew ≈ 25); the mean difference is not significant (p=0.30) and disappears under winsorization. We report medians as primary because engagement growth is extremely heavy-tailed — the standard, conservative choice for this data."*

Report medians as primary; pre-empt the mean question in a footnote/robustness line.

---

## Finding 2 — narrative_storytelling × Shares: suppression is STRONGER on the mean (corroborates the moderator synthesis)

Within each rhetorical style, Treatment−Control difference on Shares growth (winsorized):

| Rhetorical style | n (T/C) | Median diff | MWU p | **Mean diff** | **Welch p** | **Cohen d** |
|---|---|---|---|---|---|---|
| bare_assertion | 312/337 | 0 | 0.78 | +6.8 | 0.39 | +0.07 |
| emotional_appeal | 233/233 | 0 | 0.53 | +17.2 | 0.28 | +0.10 |
| **narrative_storytelling** | 39/38 | 0 | 0.034 | **−151.6** | **0.011** | **−0.62** |
| evidence_based | 8/10 | — | — | — | — | skipped (n<10) |

**What's happening:** For narrative-storytelling tweets, the Control mean Shares growth (173) is ~8× the Treatment mean (21) — a **medium-to-large effect (d = −0.62)** that the median (0 vs 0) couldn't show; only the MWU rank test caught a whisper of it (p=0.034). The mean exposes it clearly.

**Interpretation:** CN replies specifically **blunt the viral Share-upside of narrative-storytelling tweets**. The effect lives in the tail — narrative tweets that would have racked up shares don't, under Treatment — which is exactly why it shows up on the mean, not the median. This gives the moderator synthesis's "one consistent winner" a concrete mechanism: *CN suppresses the would-be-viral shares of story-form tweets.*

**Caveat:** small subgroup (n≈38/group) and one of several styles tested — report with the small-N + multiple-comparison caveat. But it corroborates the moderator synthesis from an independent (mean-based) angle, which strengthens it.

---

## Everything else — consistent null across both views

- **Likes main effect:** median diff 0 (p=0.60); raw mean −146 (p=0.19), winsorized −12 (p=0.65). Directionally Control-higher, never significant. Consistent with 8.2 (negligibly small).
- **Shares main effect:** null on every view. Consistent with 8.2 (truly null).
- **Likes per 1k Views:** median 0 (p=0.92); mean −3.0 (p=0.24). Null.
- **Shares per 1k Views:** median 0 (p=0.71); mean −1.18 (**p=0.077**). The engagement-quality hint (Treatment slightly lower) is closest to significance here on the mean — worth a one-line mention, not a headline.

---

## Bottom line

This re-analysis did its job: it found the **two** places where the mean view is informative (Views main effect = tail vs typical-tweet distinction; narrative×Shares = tail-concentrated suppression) and confirmed everything else is robust to the choice of statistic. No headline finding is overturned; the Views result is *clarified* (it's about the typical tweet) and the one moderator is *strengthened and mechanistically explained*.