"""
generate_cns.py
---------------
Generate counter-narratives (CNs) for safety metric analysis.

For each of 20 narratives × 3 KPIs:
  - Generates 3 CNs using the REFINED system prompt (agent_type='refined')
  - Generates 3 CNs using the INITIAL system prompt (agent_type='initial')

Total: 180 refined + 180 initial = 360 CNs.

Generation uses reset=False so each subsequent call within the same agent
has context of prior responses, avoiding near-duplicate CNs.

Output: safety_metrics/generated_cns.csv
  columns: claim_number, kpi, agent_type, cn_index, narrative, cn_text
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from initial_cn_agents import (
    create_pro_ukrainian_agents_gemini,
    pro_ukrainian_agents_system_prompts,
    pro_ukrainian_agents_descriptions,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(ROOT)
NARRATIVES_PATH = os.path.join(
    REPO_ROOT, "Data", "Pro Russian top users and narratives.xlsx"
)
# The post-revision prompts, i.e. the refined prompts with the naturalness and
# coherence guidelines added after the initial human validation study. These are
# the prompts the safety analysis evaluates.
REFINED_PROMPTS_PATH = os.path.join(
    ROOT, "human_validation-revised", "refined_system_prompts.xlsx"
)
OUTPUT_PATH = os.path.join(ROOT, "safety_metrics", "generated_cns.csv")

# How many CNs to generate per (narrative, KPI, agent_type)
CNS_PER_PAIR = 3

# KPI id mapping (matches kpi_id used in mini_exp_v2)
KPI_AGENT_MAP = {
    "Persuasiveness":      "CN_Creator_Agent_1",
    "Emotional Engagement": "CN_Creator_Agent_2",
    "Shareability":        "CN_Creator_Agent_3",
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
narratives = pd.read_excel(
    NARRATIVES_PATH,
    sheet_name="top_20_narratives_20250313_1716"
)["description"].tolist()

refined_prompts_df = pd.read_excel(REFINED_PROMPTS_PATH, sheet_name="Sheet1")
# Columns: ClaimNumber, KPI, SystemPrompt


def _build_history_prompt(narrative: str, previous: list[str]) -> str:
    """Appends previous CN history to the narrative input so the agent avoids repetition."""
    if not previous:
        return narrative
    history_lines = "\n".join(
        f"{i + 1}. {cn}" for i, cn in enumerate(previous)
    )
    return (
        f"{narrative}\n\n"
        "Here are your previous responses:\n"
        f"{history_lines}\n\n"
        "Think carefully through this task and make sure to generate a response "
        "different from your previous ones (in terms of structure, content, etc.) "
        "while strictly following your KEY GUIDELINES."
    )


def generate_cns_for_agent(agent, narrative: str, n: int) -> list[str]:
    """
    Run 'agent' n times against 'narrative', using accumulated history to
    encourage diversity.  Uses reset=False (stateless call — history is passed
    explicitly via the prompt rather than relying on agent memory state).
    """
    cns = []
    for _ in range(n):
        prompt = _build_history_prompt(narrative, cns)
        response = agent.run(prompt, reset=True)
        cns.append(response)
    return cns


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------
def main():
    # Resume from existing output if available (skip already-done rows)
    if os.path.exists(OUTPUT_PATH):
        existing = pd.read_csv(OUTPUT_PATH)
        done = set(
            zip(existing["claim_number"], existing["kpi"], existing["agent_type"])
        )
        rows = existing.to_dict("records")
        print(f"Resuming — {len(existing)} rows already saved, "
              f"{len(done)} (narrative, kpi, agent_type) groups done.")
    else:
        done = set()
        rows = []

    total_groups = len(narratives) * len(KPI_AGENT_MAP) * 2  # refined + initial
    completed = len(done)

    for claim_idx, narrative in enumerate(narratives, start=1):
        for kpi_name, agent_name in KPI_AGENT_MAP.items():

            for agent_type in ("initial", "refined"):
                key = (claim_idx, kpi_name, agent_type)
                if key in done:
                    continue

                print(
                    f"[{completed + 1}/{total_groups}] "
                    f"claim={claim_idx}, KPI={kpi_name}, type={agent_type}"
                )

                # Build system prompt
                if agent_type == "refined":
                    sys_prompt = refined_prompts_df[
                        (refined_prompts_df["ClaimNumber"] == claim_idx)
                        & (refined_prompts_df["KPI"] == kpi_name)
                    ]["SystemPrompt"].values[0]
                    description = f"Refined {kpi_name}-focused CN Generator Agent"
                else:
                    sys_prompt = pro_ukrainian_agents_system_prompts[agent_name]
                    description = pro_ukrainian_agents_descriptions[agent_name]

                # Create a fresh agent for this (narrative, kpi, type) group
                agents = create_pro_ukrainian_agents_gemini(
                    {agent_name: description},
                    {agent_name: sys_prompt},
                    model_name="gemini-2.5-flash",
                    temp=1.0,
                )
                agent = agents[agent_name]

                cns = generate_cns_for_agent(agent, narrative, CNS_PER_PAIR)

                for cn_idx, cn_text in enumerate(cns, start=1):
                    rows.append(
                        {
                            "claim_number": claim_idx,
                            "kpi": kpi_name,
                            "agent_type": agent_type,
                            "cn_index": cn_idx,
                            "narrative": narrative,
                            "cn_text": cn_text,
                        }
                    )

                # Save incrementally after each group
                pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
                completed += 1
                done.add(key)

    print(f"\nDone. {len(rows)} CNs saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()