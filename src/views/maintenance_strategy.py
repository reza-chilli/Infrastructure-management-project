"""Maintenance and rehabilitation strategy view."""

from __future__ import annotations

import pandas as pd
import streamlit as st


TREATMENT_ORDER = [
    "bridge_replacement",
    "heavy_rehabilitation",
    "regular_rehabilitation",
    "preventive_maintenance",
    "deferred",
]


def render_maintenance_strategy_page(
    df_processed: pd.DataFrame,
) -> None:
    """Render recommended treatments, costs, and condition outcomes."""

    st.title("Maintenance and Rehabilitation Strategy")

    st.caption(
        "Recommended interventions are based on the current BCI and "
        "component condition ratings. Treatment costs are calculated "
        "using bridge deck area and unit costs per square metre."
    )

    required_columns = [
        "Structure_ID",
        "Priority Rank",
        "Bridge_condition_Cat",
        "BCI",
        "Recommended_Treatment_Code",
        "Treatment_Name",
        "Treatment_Cost",
        "Deck_Area_m2",
        "BCI_After_Treatment",
        "BCI_Improvement",
        "Minimum_Component",
        "Minimum_Component_Condition",
        "Recommendation_Reason",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df_processed.columns
    ]

    if missing_columns:
        st.error(
            "Maintenance strategy results are missing these columns: "
            + ", ".join(missing_columns)
        )
        return

    strategy = df_processed.copy()

    strategy["Treatment_Cost"] = pd.to_numeric(
        strategy["Treatment_Cost"],
        errors="coerce",
    )

    strategy["BCI"] = pd.to_numeric(
        strategy["BCI"],
        errors="coerce",
    )

    strategy["BCI_After_Treatment"] = pd.to_numeric(
        strategy["BCI_After_Treatment"],
        errors="coerce",
    )

    strategy["BCI_Improvement"] = pd.to_numeric(
        strategy["BCI_Improvement"],
        errors="coerce",
    )

    total_bridges = len(strategy)

    total_treatment_cost = strategy["Treatment_Cost"].sum()

    average_current_bci = strategy["BCI"].mean()

    average_after_bci = strategy["BCI_After_Treatment"].mean()

    average_bci_improvement = strategy["BCI_Improvement"].mean()

    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (
        st.columns(5)
    )

    metric_col1.metric(
        "Total Bridges",
        f"{total_bridges:,}",
    )

    metric_col2.metric(
        "Recommended Treatment Cost",
        f"${total_treatment_cost:,.0f}",
    )

    metric_col3.metric(
        "Average Current BCI",
        f"{average_current_bci:.2f}",
    )

    metric_col4.metric(
        "Average BCI After Treatment",
        f"{average_after_bci:.2f}",
    )

    metric_col5.metric(
        "Average BCI Improvement",
        f"{average_bci_improvement:.2f}",
    )

    st.divider()

    st.subheader("Treatment Distribution")

    treatment_summary = (
        strategy.groupby(
            [
                "Recommended_Treatment_Code",
                "Treatment_Name",
            ],
            dropna=False,
        )
        .agg(
            Bridge_Count=(
                "Structure_ID",
                "count",
            ),
            Total_Treatment_Cost=(
                "Treatment_Cost",
                "sum",
            ),
            Average_Current_BCI=(
                "BCI",
                "mean",
            ),
            Average_BCI_After_Treatment=(
                "BCI_After_Treatment",
                "mean",
            ),
            Average_BCI_Improvement=(
                "BCI_Improvement",
                "mean",
            ),
        )
        .reset_index()
    )

    treatment_order_map = {
        treatment_code: position
        for position, treatment_code in enumerate(
            TREATMENT_ORDER
        )
    }

    treatment_summary["Treatment_Order"] = (
        treatment_summary["Recommended_Treatment_Code"]
        .map(treatment_order_map)
        .fillna(len(TREATMENT_ORDER))
    )

    treatment_summary = (
        treatment_summary
        .sort_values("Treatment_Order")
        .drop(columns="Treatment_Order")
        .reset_index(drop=True)
    )

    treatment_summary["Network_Share_Percent"] = (
        treatment_summary["Bridge_Count"]
        / total_bridges
        * 100
    )

    st.dataframe(
        treatment_summary[
            [
                "Treatment_Name",
                "Bridge_Count",
                "Network_Share_Percent",
                "Total_Treatment_Cost",
                "Average_Current_BCI",
                "Average_BCI_After_Treatment",
                "Average_BCI_Improvement",
            ]
        ],
        column_config={
            "Treatment_Name": "Recommended Treatment",
            "Bridge_Count": st.column_config.NumberColumn(
                "Bridge Count",
                format="%d",
            ),
            "Network_Share_Percent": st.column_config.NumberColumn(
                "Network Share",
                format="%.1f%%",
            ),
            "Total_Treatment_Cost": st.column_config.NumberColumn(
                "Total Cost",
                format="$%,.0f",
            ),
            "Average_Current_BCI": st.column_config.NumberColumn(
                "Average Current BCI",
                format="%.2f",
            ),
            "Average_BCI_After_Treatment": (
                st.column_config.NumberColumn(
                    "Average BCI After Treatment",
                    format="%.2f",
                )
            ),
            "Average_BCI_Improvement": (
                st.column_config.NumberColumn(
                    "Average BCI Improvement",
                    format="%.2f",
                )
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Number of Bridges by Treatment")

        bridge_count_chart = (
            treatment_summary[
                [
                    "Treatment_Name",
                    "Bridge_Count",
                ]
            ]
            .set_index("Treatment_Name")
        )

        st.bar_chart(
            bridge_count_chart,
            use_container_width=True,
        )

    with chart_col2:
        st.markdown("#### Total Cost by Treatment")

        treatment_cost_chart = (
            treatment_summary[
                [
                    "Treatment_Name",
                    "Total_Treatment_Cost",
                ]
            ]
            .set_index("Treatment_Name")
        )

        st.bar_chart(
            treatment_cost_chart,
            use_container_width=True,
        )

    st.divider()

    st.subheader("Bridge-Level Treatment Recommendations")

    treatment_options = (
        treatment_summary["Treatment_Name"]
        .dropna()
        .tolist()
    )

    condition_options = sorted(
        strategy["Bridge_condition_Cat"]
        .dropna()
        .unique()
        .tolist()
    )

    filter_col1, filter_col2 = st.columns(2)

    selected_treatments = filter_col1.multiselect(
        "Recommended Treatment",
        options=treatment_options,
        default=treatment_options,
    )

    selected_conditions = filter_col2.multiselect(
        "Current Condition Category",
        options=condition_options,
        default=condition_options,
    )

    filtered_strategy = strategy[
        strategy["Treatment_Name"].isin(
            selected_treatments
        )
        & strategy["Bridge_condition_Cat"].isin(
            selected_conditions
        )
    ].copy()

    filtered_strategy = filtered_strategy.sort_values(
        by=[
            "Priority Rank",
            "Structure_ID",
        ],
        ascending=[
            True,
            True,
        ],
    )

    st.caption(
        f"Displaying {len(filtered_strategy)} of "
        f"{len(strategy)} bridges."
    )

    display_columns = [
        "Priority Rank",
        "Structure_ID",
        "Bridge_condition_Cat",
        "BCI",
        "Minimum_Component",
        "Minimum_Component_Condition",
        "Treatment_Name",
        "Deck_Area_m2",
        "Treatment_Cost",
        "BCI_After_Treatment",
        "BCI_Improvement",
        "Recommendation_Reason",
    ]

    st.dataframe(
        filtered_strategy[display_columns],
        column_config={
            "Priority Rank": st.column_config.NumberColumn(
                "Priority Rank",
                format="%d",
            ),
            "Structure_ID": "Structure ID",
            "Bridge_condition_Cat": "Condition Category",
            "BCI": st.column_config.NumberColumn(
                "Current BCI",
                format="%.2f",
            ),
            "Minimum_Component": "Weakest Component",
            "Minimum_Component_Condition": (
                st.column_config.NumberColumn(
                    "Weakest Component Rating",
                    format="%.2f",
                )
            ),
            "Treatment_Name": "Recommended Treatment",
            "Deck_Area_m2": st.column_config.NumberColumn(
                "Deck Area",
                format="%.2f m²",
            ),
            "Treatment_Cost": st.column_config.NumberColumn(
                "Treatment Cost",
                format="$%,.0f",
            ),
            "BCI_After_Treatment": (
                st.column_config.NumberColumn(
                    "BCI After Treatment",
                    format="%.2f",
                )
            ),
            "BCI_Improvement": st.column_config.NumberColumn(
                "BCI Improvement",
                format="%.2f",
            ),
            "Recommendation_Reason": "Recommendation Reason",
        },
        use_container_width=True,
        hide_index=True,
    )

    export_columns = [
        "Priority Rank",
        "Structure_ID",
        "Bridge_Cat",
        "Unique_Span_Type",
        "Bridge_condition_Cat",
        "BCI",
        "current_Cond_Rat_Deck",
        "current_Cond_Rat_Super",
        "current_Cond_Rat_Sub",
        "Minimum_Component",
        "Minimum_Component_Condition",
        "Recommended_Treatment_Code",
        "Treatment_Name",
        "Deck_Area_m2",
        "Treatment_Cost",
        "Deck_After_Treatment",
        "Super_After_Treatment",
        "Sub_After_Treatment",
        "BCI_After_Treatment",
        "BCI_Improvement",
        "Recommendation_Reason",
    ]

    available_export_columns = [
        column
        for column in export_columns
        if column in filtered_strategy.columns
    ]

    csv_data = filtered_strategy[
        available_export_columns
    ].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Download Treatment Strategy CSV",
        data=csv_data,
        file_name="bridge_treatment_strategy.csv",
        mime="text/csv",
    )