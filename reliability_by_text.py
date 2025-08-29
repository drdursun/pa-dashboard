import pandas as pd
from scipy.stats import pointbiserialr

# 1. Load raw data
df = pd.read_excel("exam_data.xlsx")

# 2. Ensure is_correct is numeric 0/1
df["is_correct"] = df["is_correct"].astype(int)

# 3. Pivot: rows=user_id, cols=question text
pivot = df.pivot_table(
    index="user_id",
    columns="question",
    values="is_correct",
    fill_value=0
)

# 4. Compute total score per user
pivot["total_score"] = pivot.sum(axis=1)

# 5. Compute item-rest point-biserial
results = []
for q_text in pivot.columns.drop("total_score"):
    item_scores = pivot[q_text]
    rest_scores = pivot["total_score"] - item_scores

    # Skip items with zero variance
    if item_scores.nunique() < 2:
        corr, pval = None, None
    else:
        corr, pval = pointbiserialr(item_scores, rest_scores)

    results.append({
        "question": q_text,
        "point_biserial": corr,
        "p_value": pval
    })

# 6. Build DataFrame and replace None → blank/0
res_df = pd.DataFrame(results)
# 8. Format the point-biserial and p-value columns
def fmt_pb(x):
    return f"{x:.4f}"

def fmt_p(p):
    # show “<0.0001” for very small p, else 4 decimals
    return "<0.0001" if p != p or p < 0.0001 else f"{p:.4f}"

# apply formatting
res_df["point_biserial"] = res_df["point_biserial"].apply(fmt_pb)
res_df["p_value"]        = res_df["p_value"].apply(fmt_p)
res_df["p_value"] = res_df["p_value"].fillna("")
res_df["point_biserial"] = res_df["point_biserial"].fillna(0)

# 7. Save to CSV
res_df.to_csv("item_pointbiserial_by_text.csv", index=False)
print("Saved item_pointbiserial_by_text.csv")

