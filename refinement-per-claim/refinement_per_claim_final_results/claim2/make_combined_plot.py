import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

claim_str = "claim2"
base = f"refinement_per_claim_final_results/{claim_str}"

df1 = pd.read_csv(f"{base}/CN_Creator_Agent_1.csv")
df2 = pd.read_csv(f"{base}/CN_Creator_Agent_2.csv")
df3 = pd.read_csv(f"{base}/CN_Creator_Agent_3.csv")

# Each agent specializes in optimizing one KPI
series = [
    (df1, "avg_pers", "Persuasiveness (Agent 1)", "#1f77b4", "o", "-"),
    (df2, "avg_emot", "Emotional Engagement (Agent 2)", "#2ca02c", "s", "--"),
    (df3, "avg_share", "Shareability (Agent 3)", "#d62728", "^", "-."),
]

fig, ax = plt.subplots(figsize=(12, 7))

for df, avg_col, label, color, marker, ls in series:
    ax.plot(df.index, df[avg_col], linestyle=ls, marker=marker, markersize=6,
            linewidth=2, color=color, label=label)

claim_num = claim_str.replace("claim", "")
ax.set_title(f"Claim {claim_num} — KPI Average Scores per Iteration",
             fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Iteration")
ax.set_ylabel("Value")
ax.set_ylim(0, 100)
max_len = max(len(df1), len(df2), len(df3))
ax.set_xticks(np.arange(0, max_len))
ax.set_yticks(np.arange(0, 101, 10))
ax.legend()
ax.grid(True)

plt.tight_layout()
save_path = f"{base}/plot_all_kpis.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
print(f"Saved: {save_path}")
