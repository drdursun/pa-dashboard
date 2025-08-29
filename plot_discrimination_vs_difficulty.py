import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

# 1. Load your two CSVs
df_pb   = pd.read_csv("item_pointbiserial_by_text.csv")
df_diff = pd.read_csv("item_difficulty_by_question.csv", encoding="utf-8-sig")

# 2. Merge on the question text
merged = pd.merge(df_pb, df_diff, on="question", how="inner")

# 3. Ensure we have a numeric difficulty column
if merged["p_difficulty_percent"].dtype == object:
    merged["p_difficulty_num"] = (
        merged["p_difficulty_percent"]
        .str.rstrip("%")
        .astype(float) / 100
    )
else:
    merged["p_difficulty_num"] = merged["p_difficulty"]

# 4. Build the scatter plot
fig, ax = plt.subplots(figsize=(8,6))
scat = ax.scatter(
    merged["p_difficulty_num"],
    merged["point_biserial"].astype(float),
    alpha=0.7,
    edgecolor="black"
)

# 5. Reference lines & labels
ax.axvline(0.5, color="grey", linestyle="--", linewidth=1)
ax.axhline(0.3, color="grey", linestyle="--", linewidth=1)
ax.set_xlabel("Difficulty (Proportion Correct)")
ax.set_ylabel("Item-Rest Point-Biserial")
ax.set_title("Item Discrimination vs. Difficulty")

# 6. Interactive hover: show question text
cursor = mplcursors.cursor(scat, hover=True)

@cursor.connect("add")
def on_add(sel):
    # mplcursors v0.6+: sel.index is the point index
    # fallback to sel.target.index if needed
    idx = getattr(sel, "index", None)
    if idx is None:
        idx = getattr(sel.target, "index", None)
    if idx is None:
        return  # give up if we can't find an index
    text = merged["question"].iloc[idx]
    sel.annotation.set_text(text)
    # white background so text is readable
    sel.annotation.get_bbox_patch().set(fc="white")

plt.tight_layout()
plt.show()

