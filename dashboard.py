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
with st.sidebar.expander("📘 How to Read the Dashboard"):
    st.markdown("""
    ### **Item Difficulty & Discrimination Scatterplot**
    This chart shows how each PA item performs:
    - The horizontal axis represents item difficulty (percentage of students who answered correctly).
    - The vertical axis shows item discrimination (how well the item distinguishes between high- and low-performing students).

    **Example**: An item at 40% difficulty and 0.45 discrimination means that only 40% of students got it right, and the item is highly effective at separating stronger and weaker performers.

    **Interpretation**: Items in the upper-right corner (moderate difficulty, high discrimination) are ideal. Items in the lower-left (very easy or very hard, low discrimination) may need review or revision.

    ### **Item Details Table**
    This table lists each item with its text, difficulty percentage, and point-biserial discrimination score.

    Use this table to scan for items that are too easy, too hard, or not discriminating well. Sorting by each column helps identify patterns across the assessment.  
    For example, sorting by “Point-Biserial” from lowest to highest can quickly surface items that do not differentiate well between high- and low-performing students — such as an item with a discrimination score below 0.1, which may need revision or removal.

    **Example**: Suppose Item 12 has a difficulty of 78% and a point-biserial of 0.08. This means most students answered it correctly, but it does not effectively distinguish between stronger and weaker performers.

    **What Point-Biserial Means**:  
    Point-biserial is a statistical measure that shows how well an item correlates with overall performance. A higher score (e.g., 0.4 or above) means students who did well on the PA were more likely to get the item right, and those who struggled were more likely to miss it.

    ### **Difficulty & Discrimination Filters**
    These sliders help focus on specific subsets of items:
    - Difficulty Range filters items based on how easy or hard they are.
    - Discrimination Range filters items based on how well they differentiate student performance.

    **Example**: Setting difficulty to 30–70% and discrimination to 0.3–0.6 will isolate items that are moderately challenging and highly informative.

    To identify poor-performing items, try setting the difficulty range to very low (e.g., 0–20%) or very high (e.g., 80–100%), and the discrimination range to low values (e.g., 0.0–0.2).

    ### **Distractor Analysis**
    This section evaluates how students responded to each option in a selected PA item, focusing on the effectiveness of incorrect choices (distractors).

    It includes:
    - A bar chart showing how often each option was selected and how often it was correct.
    - A table showing total selections, number correct, selection rate, and correctness rate for each option.

    **How to Interpret Distractors**

    | Distractor Type         | Selection Rate | Correctness Rate | Interpretation                                      |
    |-------------------------|----------------|------------------|-----------------------------------------------------|
    | Effective               | 10–40%         | ~0%              | Attracts lower-performing students appropriately    |
    | Weak                    | <5%            | ~0%              | Rarely chosen; offers little diagnostic value       |
    | Misleading              | >40%           | ~0%              | Over-chosen; may confuse high performers            |
    | Ambiguous or flawed     | Any            | >5%              | Incorrect but frequently marked correct; needs review

    **Example**:  
    If Option B was selected by 60% of students and only 10% of those got it right, it may be misleading or poorly worded.  
    If Option D was selected by just 2% of students and never correct, it may be too implausible to be useful.
    """)

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

st.markdown("---")  # horizontal separator

# 1) Reading Passages CEFR Distribution
st.header("Reading Passages CEFR Distribution")
st.image("images/reading_passages_cefr_distribution.png", use_container_width=True)

# 2) Reading Question CEFR Distribution
st.header("Reading Question CEFR Distribution")
st.image("images/reading_questions_cefr_distribution.png", use_container_width=True)

# 3) Passage vs Question CEFR Levels with Collapsible How-To Sidebar
with st.sidebar.expander("How to Interpret the Passage vs Question Heatmap", expanded=False):
    st.markdown(
        """
1. Axes  
   * The vertical axis lists the CEFR levels assigned to each passage (from Pre-A1 up to C1).  
   * The horizontal axis lists the CEFR levels assigned to each question under those passages.  

2. Cells & Color Intensity  
   * Each cell’s number is the count of question–passage pairs that share that combination of predicted levels.  
   * Darker (warmer) colors mean more items fell into that cell; lighter (cooler) colors mean fewer.  

3. The Diagonal  
   * Cells along the diagonal (where passage level = question level) show how often questions landed in the same band as their passage.  
   * A strong diagonal indicates that question difficulty generally matches passage difficulty.  

4. Off-Diagonal Patterns  
   * Cells above the diagonal (passage level < question level) flag questions predicted harder than their passage.  
   * Cells below the diagonal (passage level > question level) flag questions predicted easier than their passage.  

5. Row & Column Reads  
   * Reading across a single row shows the distribution of question levels for one passage level.  
     For example, the “B1” row tells you: out of all B1 passages, how many questions were tagged A2, B1, B2, etc.  
   * Reading down a column shows where questions at a given level came from in terms of passage levels.  
     For example, the “A2+” column tells you: of all A2+ questions, how many were written under passages of each level.
        """
    )

st.header("Passage vs Question CEFR Levels")
st.image("images/passage_question_cefr_heatmap.png", use_container_width=True)


