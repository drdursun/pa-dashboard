import pandas as pd

# 1. Load the Excel file
df = pd.read_excel("exam_data.xlsx")

# 2. Convert boolean is_correct to integer 0/1
df["is_correct"] = df["is_correct"].astype(int)

# 3. Aggregate by question across all versions
question_agg = (
    df
    .groupby("question")
    .agg(
        total_responses=("is_correct", "count"),
        total_correct  =("is_correct", "sum")
    )
    .reset_index()
)

# 4. Compute item difficulty p = total_correct / total_responses
# Compute raw proportion correct
question_agg["p_difficulty"] = (
    question_agg["total_correct"]
    / question_agg["total_responses"]
)

# Round proportion to three decimals
question_agg["p_difficulty"] = question_agg["p_difficulty"].round(3)

# Add a percentage string (one decimal place)
question_agg["p_difficulty_percent"] = (
    (question_agg["p_difficulty"] * 100)
    .round(1)
    .astype(str) + "%"
)

# 5. Save the results
question_agg.to_csv(
    "item_difficulty_by_question.csv",
    index=False,
    encoding="utf-8-sig"
)
print("Saved item_difficulty_by_question.csv")


