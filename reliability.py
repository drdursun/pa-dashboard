import pandas as pd
import pingouin as pg
from scipy.stats import pointbiserialr

# 1. Load raw item-level data
df = pd.read_excel("exam_data.xlsx")

# 2. Ensure is_correct is numeric 0/1
df["score"] = df["is_correct"].astype(int)

# 3. Pivot to wide format: rows=user_id, cols=question_number
wide = df.pivot_table(
    index="user_id",
    columns="question_number",
    values="score",
    fill_value=0
)

# 4. Cronbach’s alpha
alpha, _ = pg.cronbach_alpha(data=wide)
print(f"Cronbach’s alpha: {alpha:.3f}")

# 5. Compute point-biserial correlations
total_score = wide.sum(axis=1)
results = []
for qnum in wide.columns:
    corr, pval = pointbiserialr(wide[qnum], total_score)
    results.append({
        "question_number": qnum,
        "point_biserial": corr,
        "p_value": pval
    })

pb_df = pd.DataFrame(results)
pb_df.to_csv("item_pointbiserial.csv", index=False)
print("Point-biserial correlations saved to item_pointbiserial.csv")

