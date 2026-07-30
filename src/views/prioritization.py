import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def render_prioritization_page(
    df_processed: pd.DataFrame,
    top10: pd.DataFrame,
) -> None:
    """Render the bridge prioritization page."""

    st.title("Development of a Prioritization Framework")

    st.caption(
        "Bridges are ranked using condition, traffic volume, "
        "and replacement cost criteria."
    )

    priority_weights = st.session_state.get(
        "Priority_Weights",
        {
            "bci": 0.50,
            "traffic": 0.30,
            "replacement_cost": 0.20,
        },
    )

    w_bci = priority_weights.get("bci", 0.50)
    w_traffic = priority_weights.get("traffic", 0.30)
    w_cost = priority_weights.get("replacement_cost", 0.20)

    weight_sum = w_bci + w_traffic + w_cost

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Condition Weight",
        f"{w_bci:.0%}",
    )

    col2.metric(
        "Traffic Weight",
        f"{w_traffic:.0%}",
    )

    col3.metric(
        "Replacement Cost Weight",
        f"{w_cost:.0%}",
    )

    col4.metric(
        "Total Weight",
        f"{weight_sum:.0%}",
    )

    st.info(
        "Priority Score = "
        f"({w_bci:.0%} × Condition Score) + "
        f"({w_traffic:.0%} × Traffic Score) + "
        f"({w_cost:.0%} × Cost Score)"
    )

    if not np.isclose(weight_sum, 1.0):
        st.error(
            "The prioritization weights must add up to 100%. "
            f"Current total: {weight_sum:.1%}"
        )
        return

    if top10.empty:
        st.warning("No prioritization results are available.")
        return

    required_columns = [
        "Priority Rank",
        "Structure_ID",
        "Bridge_Cat",
        "Unique_Span_Type",
        "BCI",
        "Condition_Score",
        "Traffic_Volume",
        "Traffic_Score",
        "Replacement_Cost",
        "Cost_Score",
        "Priority Score",
        "Bridge_condition_Cat",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in top10.columns
    ]

    if missing_columns:
        st.error(
            "The prioritization output is missing these columns: "
            + ", ".join(missing_columns)
        )
        return

    top10_table = top10[required_columns].copy()

    st.subheader("Top 10 Priority Bridges")

    st.dataframe(
        top10_table,
        column_config={
            "Priority Rank": st.column_config.NumberColumn(
                "Rank",
                format="%d",
            ),
            "Structure_ID": "Structure ID",
            "Bridge_Cat": "Bridge Category",
            "Unique_Span_Type": "Span Type",
            "BCI": st.column_config.NumberColumn(
                "BCI",
                format="%.2f",
            ),
            "Condition_Score": st.column_config.NumberColumn(
                "Condition Score",
                format="%.2f",
            ),
            "Traffic_Volume": st.column_config.NumberColumn(
                "Traffic Volume",
                format="%,d",
            ),
            "Traffic_Score": st.column_config.NumberColumn(
                "Traffic Score",
                format="%.2f",
            ),
            "Replacement_Cost": st.column_config.NumberColumn(
                "Replacement Cost",
                format="$%,.0f",
            ),
            "Cost_Score": st.column_config.NumberColumn(
                "Cost Score",
                format="%.2f",
            ),
            "Priority Score": st.column_config.NumberColumn(
                "Priority Score",
                format="%.2f",
            ),
            "Bridge_condition_Cat": "Condition Category",
        },
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top 10 Bridges by Priority Score")

    chart_data = top10_table[
        [
            "Structure_ID",
            "Priority Score",
        ]
    ].copy()

    # Ascending order makes the highest score appear at the top
    # of a horizontal bar chart.
    chart_data = chart_data.sort_values(
        by="Priority Score",
        ascending=True,
    )

    chart_data["Structure_ID"] = (
        chart_data["Structure_ID"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(
        chart_data["Structure_ID"],
        chart_data["Priority Score"],
    )

    ax.set_title("Top 10 Priority Bridges")
    ax.set_xlabel("Priority Score")
    ax.set_ylabel("Structure ID")

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.3,
    )

    ax.bar_label(
        bars,
        fmt="%.2f",
        padding=3,
    )

    max_score = chart_data["Priority Score"].max()

    if pd.notna(max_score):
        ax.set_xlim(
            0,
            max(100, max_score * 1.12),
        )

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)

    st.subheader("Complete Bridge Priority Ranking")

    full_ranking_columns = [
        "Priority Rank",
        "Structure_ID",
        "Bridge_Cat",
        "Unique_Span_Type",
        "BCI",
        "Bridge_condition_Cat",
        "Condition_Score",
        "Traffic_Volume",
        "Traffic_Score",
        "Replacement_Cost",
        "Cost_Score",
        "Priority Score",
    ]

    missing_full_columns = [
        column
        for column in full_ranking_columns
        if column not in df_processed.columns
    ]

    if missing_full_columns:
        st.error(
            "The complete ranking is missing these columns: "
            + ", ".join(missing_full_columns)
        )
        return

    full_ranking = (
        df_processed[full_ranking_columns]
        .sort_values(
            by=[
                "Priority Rank",
                "Structure_ID",
            ],
            ascending=[
                True,
                True,
            ],
        )
        .copy()
    )

    filter_col1, filter_col2 = st.columns(2)

    condition_options = sorted(
        full_ranking["Bridge_condition_Cat"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_conditions = filter_col1.multiselect(
        "Condition Category",
        options=condition_options,
        default=condition_options,
    )

    bridge_category_options = sorted(
        full_ranking["Bridge_Cat"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_bridge_categories = filter_col2.multiselect(
        "Bridge Category",
        options=bridge_category_options,
        default=bridge_category_options,
    )

    filtered_ranking = full_ranking[
        full_ranking["Bridge_condition_Cat"].isin(
            selected_conditions
        )
        & full_ranking["Bridge_Cat"].isin(
            selected_bridge_categories
        )
    ].copy()

    st.caption(
        f"Displaying {len(filtered_ranking)} of "
        f"{len(full_ranking)} bridges."
    )

    st.dataframe(
        filtered_ranking,
        column_config={
            "Priority Rank": st.column_config.NumberColumn(
                "Rank",
                format="%d",
            ),
            "Structure_ID": "Structure ID",
            "Bridge_Cat": "Bridge Category",
            "Unique_Span_Type": "Span Type",
            "BCI": st.column_config.NumberColumn(
                "BCI",
                format="%.2f",
            ),
            "Bridge_condition_Cat": "Condition Category",
            "Condition_Score": st.column_config.NumberColumn(
                "Condition Score",
                format="%.2f",
            ),
            "Traffic_Volume": st.column_config.NumberColumn(
                "Traffic Volume",
                format="%,d",
            ),
            "Traffic_Score": st.column_config.NumberColumn(
                "Traffic Score",
                format="%.2f",
            ),
            "Replacement_Cost": st.column_config.NumberColumn(
                "Replacement Cost",
                format="$%,.0f",
            ),
            "Cost_Score": st.column_config.NumberColumn(
                "Cost Score",
                format="%.2f",
            ),
            "Priority Score": st.column_config.NumberColumn(
                "Priority Score",
                format="%.2f",
            ),
        },
        use_container_width=True,
        hide_index=True,
    )