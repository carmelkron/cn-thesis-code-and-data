import os
import pandas as pd

# Resolve everything against this file's own directory, so the script runs from
# any working directory.
HERE = os.path.dirname(os.path.abspath(__file__))

data = []

for i in range(1, 21):
    filename = os.path.join(HERE, f"claim{i}.py")
    if not os.path.exists(filename):
        continue
    local_vars = {}
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
        exec(code, {}, local_vars)
    mapping = {
        "agent_1": "Persuasiveness",
        "agent_2": "Emotional Engagement",
        "agent_3": "Shareability"
    }
    for var, kpi in mapping.items():
        if var in local_vars:
            data.append({
                "ClaimNumber": i,
                "KPI": kpi,
                "SystemPrompt": local_vars[var]
            })

df = pd.DataFrame(data, columns=["ClaimNumber", "KPI", "SystemPrompt"])
df.to_excel(os.path.join(HERE, "system_prompts.xlsx"), index=False)