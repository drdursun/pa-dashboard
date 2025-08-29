import pandas as pd

# Load per-question difficulty
df = pd.read_csv("item_difficulty_by_question.csv")

# Sort ascending → hardest first; take bottom 10
hardest = df.sort_values("p_difficulty").head(10)
hardest.to_csv("10_hardest_questions.csv", index=False)

# Sort descending → easiest first; take top 10
easiest = df.sort_values("p_difficulty", ascending=False).head(10)
easiest.to_csv("10_easiest_questions.csv", index=False)

print("10 hardest → 10_hardest_questions.csv")
print("10 easiest → 10_easiest_questions.csv")

