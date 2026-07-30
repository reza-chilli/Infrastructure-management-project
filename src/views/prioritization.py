import streamlit as st
import pandas as pd


def render_prioritization_page(
    top10: pd.DataFrame,
) -> None:
    """Render the bridge prioritization page."""

    st.title("Development of a Prioritization Framework")

    st.caption(
        "Bridges are ranked using condition, traffic volume, "
        "and replacement cost criteria."
    )

    if top10.empty:
        st.warning("No prioritization results are available.")
        return

    required_columns = [
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

    top10_table.insert(
        0,
        "Priority Rank",
        range(1, len(top10_table) + 1),
    )

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