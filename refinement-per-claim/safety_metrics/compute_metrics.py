"""
compute_metrics.py
------------------
Compute 4 safety metrics on all generated CNs AND on two external human
CN baselines (MT-CONAN and CONAN).

Metrics
-------
All four metrics directly address the reviewer's concern that generated messages
may be "toxic, overly aggressive, or might backfire and make things worse."

1. Toxicity       — Detoxify 'original' model (unitary/toxic-bert)
                    Citation: Hanu & Unitary team (2020), Detoxify, GitHub
                    Score: results['toxicity']  ∈ [0, 1]
                    Addresses: general harmful content

2. Insult         — Detoxify 'original' model (same as above, no extra cost)
                    Citation: Hanu & Unitary team (2020), Detoxify, GitHub
                    Score: results['insult']  ∈ [0, 1]
                    Addresses: "overly aggressive" language

3. Threat         — Detoxify 'original' model (same as above, no extra cost)
                    Citation: Hanu & Unitary team (2020), Detoxify, GitHub
                    Score: results['threat']  ∈ [0, 1]
                    Addresses: threatening tone that "might backfire"

4. Offensiveness  — cardiffnlp/twitter-roberta-base-offensive
                    Citation: Barbieri et al. (2020), TweetEval, EMNLP Findings
                    Score: P("OFF")  ∈ [0, 1]
                    Addresses: offensive language; Twitter-trained model is ideal
                    for our 280-character tweet-format CNs

Baselines
---------
  CONAN     : Chung et al. (2019), ACL 2019
  MT-CONAN  : Fanton et al. (2021), ACL 2021
  Source: https://github.com/marcoguerini/CONAN

Outputs
-------
  safety_metrics/cn_scores.csv        — generated CNs with metric scores
  safety_metrics/baseline_scores.csv  — baseline CNs with metric scores
"""

import os
import urllib.request

# Suppress duplicate OpenMP DLL warning common in Anaconda + PyTorch environments
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd
import torch
from detoxify import Detoxify
from transformers import pipeline

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_CSV = os.path.join(ROOT, "safety_metrics", "generated_cns.csv")
SCORES_CSV = os.path.join(ROOT, "safety_metrics", "cn_scores.csv")
BASELINE_CSV = os.path.join(ROOT, "safety_metrics", "baseline_scores.csv")

BASELINE_SAMPLE_SIZE = 180  # match our generated CN count per comparison group

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
DEVICE = 0 if torch.cuda.is_available() else -1
print(f"Using device: {'GPU' if DEVICE == 0 else 'CPU'}")


def load_models():
    print("Loading models...")

    # Detoxify 'original' covers toxicity, insult, and threat — single model, one citation.
    toxicity_model = Detoxify("original")

    # TweetEval offensive model — ideal for 280-char tweet-format CNs.
    offensive_pipe = pipeline(
        "text-classification",
        model="cardiffnlp/twitter-roberta-base-offensive",
        device=DEVICE,
        top_k=None,
    )

    print("All models loaded.")
    return toxicity_model, offensive_pipe


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------
def _label_score(results: list[dict], target_label: str) -> float:
    """
    Extract the probability for 'target_label' from a pipeline result.

    'results' is a list of {'label': str, 'score': float} dicts returned
    when top_k=None.  Comparison is case-insensitive.
    """
    target = target_label.lower()
    for item in results:
        if item["label"].lower() == target:
            return float(item["score"])
    # Fallback: return score of whichever label contains the target string
    for item in results:
        if target in item["label"].lower():
            return float(item["score"])
    raise ValueError(
        f"Label '{target_label}' not found in results: "
        + str([r["label"] for r in results])
    )


def score_texts(texts: list[str], toxicity_model, offensive_pipe) -> pd.DataFrame:
    """
    Score a list of texts on all 4 metrics.
    Returns a DataFrame with columns: cn_text, toxicity, insult, threat, offensiveness
    """
    print(f"  Scoring {len(texts)} texts...")

    # --- Detoxify: toxicity, insult, threat (single model, one pass) ---
    tox_results = toxicity_model.predict(texts)  # returns dict of lists
    toxicity_scores = list(tox_results["toxicity"])
    insult_scores   = list(tox_results["insult"])
    threat_scores   = list(tox_results["threat"])

    # --- Offensiveness (TweetEval, Twitter-trained) ---
    off_results = offensive_pipe(texts, batch_size=16, truncation=True, max_length=512)
    off_scores  = [_label_score(r, "OFF") for r in off_results]

    return pd.DataFrame(
        {
            "cn_text":       texts,
            "toxicity":      toxicity_scores,
            "insult":        insult_scores,
            "threat":        threat_scores,
            "offensiveness": off_scores,
        }
    )


# ---------------------------------------------------------------------------
# Baseline loading
# ---------------------------------------------------------------------------
# CSV is simpler and more reliable than JSON for both datasets.
# Column names confirmed from the actual files in marcoguerini/CONAN repo.
BASELINE_SOURCES = {
    "CONAN": {
        "url": (
            "https://raw.githubusercontent.com/marcoguerini/CONAN/master/"
            "CONAN/CONAN.csv"
        ),
        "cn_col": "counterSpeech",
    },
    "MT-CONAN": {
        "url": (
            "https://raw.githubusercontent.com/marcoguerini/CONAN/master/"
            "Multitarget-CONAN/Multitarget-CONAN.csv"
        ),
        "cn_col": "COUNTER_NARRATIVE",
    },
}


def _fetch_csv(url: str, cn_col: str) -> list[str]:
    """Download a CSV from url and return the list of non-empty strings in cn_col."""
    import io
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8")
    df = pd.read_csv(io.StringIO(content))
    texts = df[cn_col].dropna().astype(str).str.strip()
    return [t for t in texts if t]


def load_baseline_cns() -> pd.DataFrame:
    """
    Download CONAN and MT-CONAN CSVs from GitHub and extract CN texts.
    Returns a DataFrame with columns: source, cn_text
    Uses a local cache (CSV per source) to avoid re-downloading.
    """
    import random
    rng = random.Random(42)
    rows = []

    for source, cfg in BASELINE_SOURCES.items():
        cache_path = os.path.join(ROOT, "safety_metrics", f"baseline_{source}.csv")

        if os.path.exists(cache_path):
            print(f"  {source}: loading from local cache...")
            cached_df = pd.read_csv(cache_path)
            cn_texts = cached_df["cn_text"].tolist()
            print(f"  {source}: {len(cn_texts)} CNs in cache.")
        else:
            print(f"  Downloading {source}...")
            try:
                cn_texts = _fetch_csv(cfg["url"], cfg["cn_col"])
                # Save cache
                pd.DataFrame({"cn_text": cn_texts}).to_csv(cache_path, index=False)
                print(f"  {source}: downloaded {len(cn_texts)} CNs.")
            except Exception as e:
                print(f"  WARNING: Could not download {source}: {e}")
                continue

        if not cn_texts:
            print(f"  WARNING: No CN texts found in {source}.")
            continue

        if len(cn_texts) > BASELINE_SAMPLE_SIZE:
            cn_texts = rng.sample(cn_texts, BASELINE_SAMPLE_SIZE)

        for text in cn_texts:
            rows.append({"source": source, "cn_text": text})

        print(f"  {source}: using {len(cn_texts)} CNs.")

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # --- Load generated CNs ---
    if not os.path.exists(GENERATED_CSV):
        raise FileNotFoundError(
            f"Generated CNs not found at {GENERATED_CSV}. "
            "Run generate_cns.py first."
        )
    gen_df = pd.read_csv(GENERATED_CSV)
    print(f"Loaded {len(gen_df)} generated CNs.")

    # --- Load models ---
    toxicity_model, offensive_pipe = load_models()

    # --- Score generated CNs ---
    if os.path.exists(SCORES_CSV):
        print(f"Scores file already exists at {SCORES_CSV}. Skipping generation scoring.")
        scored_gen = pd.read_csv(SCORES_CSV)
    else:
        print("\nScoring generated CNs...")
        metric_df = score_texts(
            gen_df["cn_text"].tolist(),
            toxicity_model, offensive_pipe,
        )
        # Merge scores back with metadata
        scored_gen = gen_df.reset_index(drop=True).join(
            metric_df.drop(columns=["cn_text"])
        )
        scored_gen.to_csv(SCORES_CSV, index=False)
        print(f"Saved scored CNs to {SCORES_CSV}")

    # --- Load & score baselines ---
    if os.path.exists(BASELINE_CSV):
        print(f"\nBaseline scores already exist at {BASELINE_CSV}. Skipping.")
    else:
        print("\nLoading baseline datasets...")
        baseline_df = load_baseline_cns()

        if baseline_df.empty:
            print("WARNING: No baseline CNs loaded. Skipping baseline scoring.")
        else:
            print("\nScoring baseline CNs...")
            baseline_metrics = score_texts(
                baseline_df["cn_text"].tolist(),
                toxicity_model, offensive_pipe,
            )
            scored_baseline = baseline_df.reset_index(drop=True).join(
                baseline_metrics.drop(columns=["cn_text"])
            )
            scored_baseline.to_csv(BASELINE_CSV, index=False)
            print(f"Saved baseline scores to {BASELINE_CSV}")

    print("\nAll done.")


if __name__ == "__main__":
    main()
