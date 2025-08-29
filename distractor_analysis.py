import pandas as pd

# 1. Load only the columns we need, using user_id to identify students
df = pd.read_excel(
    "exam_data.xlsx",
    usecols=["question", "user_answer", "user_id", "is_correct", "correct_answer"]
)

# 2. Coerce types
df["user_answer"] = df["user_answer"].astype(str)
df["is_correct"]   = df["is_correct"].astype(int)

# 3. Pivot to count unique students who selected each option
sel = pd.pivot_table(
    df,
    index=["question", "user_answer"],
    values="user_id",
    aggfunc=pd.Series.nunique,
    fill_value=0
).rename(columns={"user_id": "total_selected"}).reset_index()

# 4. Pivot to count unique students who selected each option AND were correct
correct_df = df[df["is_correct"] == 1]
cor = pd.pivot_table(
    correct_df,
    index=["question", "user_answer"],
    values="user_id",
    aggfunc=pd.Series.nunique,
    fill_value=0
).rename(columns={"user_id": "total_correct"}).reset_index()

# 5. Merge selection counts and correct counts
analysis = sel.merge(
    cor,
    on=["question", "user_answer"],
    how="left"
)
analysis["total_correct"] = analysis["total_correct"].fillna(0).astype(int)

# 6. Compute total unique students per question
total = (
    df.groupby("question")["user_id"]
      .nunique()
      .rename("total_responses")
      .reset_index()
)
analysis = analysis.merge(total, on="question", how="left")

# 7. Calculate percentages (rounded to three decimals)
analysis["pct_selected"] = (
    analysis["total_selected"] 
    / analysis["total_responses"]
).round(3)

analysis["pct_correct"] = (
    analysis["total_correct"]  
    / analysis["total_selected"]
).fillna(0).round(3)
# 8. Pull each question's correct answer into the table
correct_opts = (
    df[["question", "correct_answer"]]
    .drop_duplicates(subset=["question"])
)
analysis = analysis.merge(
    correct_opts,
    on="question",
    how="left"
)
# 9. Blank out repeated correct_answer values (only keep first per question)
analysis["correct_answer"] = analysis["correct_answer"].mask(
    analysis["question"].duplicated(),
    ""
)

# 8. Save the result
analysis.to_csv("distractor_analysis.csv", index=False)
print("Saved distractor_analysis.csv")

