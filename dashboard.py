import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Define relative path to data folder
data_dir = "data"

# ──────────────────────────────────────────
# 1. Load & Prepare Difficulty/Discrimination Data
# ──────────────────────────────────────────

# Read point-biserial and difficulty
df_pb   = pd.read_csv(os.path.join(data_dir, "item_pointbiserial_by_text.csv"))
df_diff = pd.read_csv(os.path.join(data_dir, "item_difficulty_by_question.csv"), encoding="utf-8-sig")

# Derive numeric difficulty percentage (0–100)
if "p_difficulty_percent" in df_diff.columns:
    if df_diff["p_difficulty_percent"].dtype == object:
        df_diff["p_diff_pct"] = (
            df_diff["p_difficulty_percent"].str.rstrip("%").astype(float)
        )
    else:
        df_diff["p_diff_pct"] = df_diff["p_difficulty_percent"].astype(float)
elif "p_difficulty" in df_diff.columns:
    df_diff["p_diff_pct"] = df_diff["p_difficulty"].astype(float) * 100
else:
    raise KeyError("Cannot find a difficulty column in item_difficulty_by_question.csv")

# Merge on question text
merged = pd.merge(df_pb, df_diff, on="question", how="inner")

# ──────────────────────────────────────────
# 2. Sidebar: Filters for Diff & Disc
# ──────────────────────────────────────────

st.sidebar.title("Filter Items")

min_diff, max_diff = st.sidebar.slider(
    "Difficulty (%) range",
    float(merged["p_diff_pct"].min()),
    float(merged["p_diff_pct"].max()),
    (0.0, 100.0)
)

min_dis, max_dis = st.sidebar.slider(
    "Discrimination range",
    float(merged["point_biserial"].min()),
    float(merged["point_biserial"].max()),
    (float(merged["point_biserial"].min()), float(merged["point_biserial"].max())),
    step=0.01
)

# Apply filters
df_fd = merged[
    (merged["p_diff_pct"]   >= min_diff) &
    (merged["p_diff_pct"]   <= max_diff) &
    (merged["point_biserial"] >= min_dis) &
    (merged["point_biserial"] <= max_dis)
]

# ──────────────────────────────────────────
# 3. Main View: Scatter & Item Table
# ──────────────────────────────────────────

st.title("Item Difficulty & Discrimination Explorer")
st.write(f"Showing {len(df_fd)} of {len(merged)} items")

# Scatter plot
fig = px.scatter(
    df_fd,
    x="p_diff_pct",
    y="point_biserial",
    hover_name="question",
    hover_data={
        "p_diff_pct": True,
        "point_biserial": True
    },
    labels={
        "p_diff_pct": "Difficulty (%)",
        "point_biserial": "Point-Biserial"
    },
    title="Discrimination vs Difficulty"
)
fig.add_vline(x=50, line_dash="dash", line_color="grey")
fig.add_hline(y=0.3, line_dash="dash", line_color="grey")
st.plotly_chart(fig, use_container_width=True)

# Item details table
st.subheader("Item Details")
st.dataframe(
    df_fd[[
        "question",
        "p_diff_pct",
        "point_biserial"
    ]].rename(columns={
        "question": "Question",
        "p_diff_pct": "Difficulty (%)",
        "point_biserial": "Point-Biserial"
    }),
    use_container_width=True
)

# ──────────────────────────────────────────
# 4. Load Distractor Analysis & Sidebar Selector
# ──────────────────────────────────────────

distr = pd.read_csv(os.path.join(data_dir, "distractor_analysis.csv"))
st.sidebar.markdown("---")
question_list = sorted(distr["question"].unique())
sel_q = st.sidebar.selectbox("Select Question for Distractor Analysis", question_list)

# ──────────────────────────────────────────
# 5. Distractor Bar Chart & Table
# ──────────────────────────────────────────

sub = distr[distr["question"] == sel_q]

st.subheader("Distractor Analysis for:")
st.markdown(f"**{sel_q}**")

# Bar chart of selection rates (colored by correctness rate)
fig2 = px.bar(
    sub,
    x="user_answer",
    y="pct_selected",
    color="pct_correct",
    color_continuous_scale=["red", "green"],
    hover_data=["total_selected", "total_correct", "pct_correct"],
    labels={
        "user_answer": "Option",
        "pct_selected": "Selection Rate",
        "pct_correct": "Correct Rate"
    },
    title="Option Selection & Correctness"
)
st.plotly_chart(fig2, use_container_width=True)

# Detailed metrics table
st.subheader("Detailed Distractor Metrics")
st.dataframe(
    sub[[
        "user_answer",
        "total_selected",
        "total_correct",
        "pct_selected",
        "pct_correct"
    ]].rename(columns={
        "user_answer": "Option",
        "total_selected": "Selected",
        "total_correct": "Correct",
        "pct_selected": "Sel Rate",
        "pct_correct": "Corr Rate"
    }),
    use_container_width=True
)

