"""Maintenance strategy and five-year investment planning view."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.five_year_plan import run_budget_scenarios
from src.treatments import treatment_catalog_as_records


TREATMENT_ORDER = [
    "preventive_maintenance",
    "regular_rehabilitation",
    "heavy_rehabilitation",
    "bridge_replacement",
    "deferred",
]


def render_maintenance_strategy_page(
    df_processed: pd.DataFrame,
    current_year: int,
    workbook_path: str | Path,
) -> None:
    """Render current treatment needs and five-year budget scenarios."""

    st.title("Maintenance and Rehabilitation Strategy")
    st.caption(
        "Current recommendations show unconstrained engineering need. "
        "The five-year plan then determines which actions can actually be "
        "programmed under baseline and constrained annual budgets."
    )

    required_columns = [
        "Structure_ID",
        "Priority Rank",
        "Bridge_condition_Cat",
        "BCI",
        "Recommended_Treatment_Code",
        "Treatment_Name",
        "Treatment_Cost",
        "BCI_After_Treatment",
        "BCI_Improvement",
    ]
    missing = [column for column in required_columns if column not in df_processed]
    if missing:
        st.error(
            "Maintenance strategy results are missing these columns: "
            + ", ".join(missing)
        )
        return

    strategy = df_processed.copy()
    for column in [
        "Treatment_Cost",
        "BCI",
        "BCI_After_Treatment",
        "BCI_Improvement",
    ]:
        strategy[column] = pd.to_numeric(strategy[column], errors="coerce")

    treatment_summary = _build_current_treatment_summary(strategy)

    st.subheader("Current Unconstrained Treatment Need")
    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Bridges", f"{len(strategy):,}")
    metric2.metric(
        "Current Recommended Cost",
        f"${strategy['Treatment_Cost'].sum():,.0f}",
    )
    metric3.metric("Average Current BCI", f"{strategy['BCI'].mean():.2f}")
    metric4.metric(
        "Average BCI After Recommended Actions",
        f"{strategy['BCI_After_Treatment'].mean():.2f}",
    )

    st.dataframe(
        treatment_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Treatment_Name": "Action",
            "Bridge_Count": st.column_config.NumberColumn(
                "Bridge Count",
                format="%d",
            ),
            "Network_Share_Percent": st.column_config.NumberColumn(
                "Network Share",
                format="%.1f%%",
            ),
            "Total_Treatment_Cost": st.column_config.NumberColumn(
                "Current Need Cost",
                format="$%,.0f",
            ),
            "Average_Current_BCI": st.column_config.NumberColumn(
                "Average Current BCI",
                format="%.2f",
            ),
            "Average_BCI_After_Treatment": st.column_config.NumberColumn(
                "Average BCI After Action",
                format="%.2f",
            ),
        },
    )

    st.caption(
        "All five action categories are shown. Empty categories have zero "
        "bridges and zero cost; their average BCI remains blank rather than "
        "being incorrectly reported as zero."
    )

    st.divider()
    _render_five_year_section(
        strategy=strategy,
        current_year=current_year,
        workbook_path=workbook_path,
    )


def _build_current_treatment_summary(strategy: pd.DataFrame) -> pd.DataFrame:
    """Summarize current recommendations while retaining all five actions."""

    catalog = pd.DataFrame(treatment_catalog_as_records())[
        ["Treatment_Code", "Treatment_Name"]
    ].rename(columns={"Treatment_Code": "Recommended_Treatment_Code"})

    summary = (
        strategy.groupby(
            ["Recommended_Treatment_Code", "Treatment_Name"],
            dropna=False,
        )
        .agg(
            Bridge_Count=("Structure_ID", "count"),
            Total_Treatment_Cost=("Treatment_Cost", "sum"),
            Average_Current_BCI=("BCI", "mean"),
            Average_BCI_After_Treatment=("BCI_After_Treatment", "mean"),
        )
        .reset_index()
    )

    summary = catalog.merge(
        summary,
        on=["Recommended_Treatment_Code", "Treatment_Name"],
        how="left",
    )
    summary["Bridge_Count"] = summary["Bridge_Count"].fillna(0).astype(int)
    summary["Total_Treatment_Cost"] = summary[
        "Total_Treatment_Cost"
    ].fillna(0.0)
    summary["Network_Share_Percent"] = (
        summary["Bridge_Count"] / max(len(strategy), 1) * 100.0
    )

    order_map = {code: index for index, code in enumerate(TREATMENT_ORDER)}
    summary["_order"] = summary["Recommended_Treatment_Code"].map(order_map)
    return (
        summary.sort_values("_order")
        .drop(columns=["_order", "Recommended_Treatment_Code"])
        .reset_index(drop=True)
    )


def _render_five_year_section(
    strategy: pd.DataFrame,
    current_year: int,
    workbook_path: str | Path,
) -> None:
    st.subheader("Five-Year Investment Plan")
    st.caption(
        "Year 1 uses the current calculated condition. Before each later year, "
        "one year of deterioration is applied and traffic grows by 6%. "
        "Bridges are reprioritized annually and funded in priority order."
    )

    current_non_deferred_need = strategy.loc[
        strategy["Recommended_Treatment_Code"] != "deferred",
        "Treatment_Cost",
    ].sum()
    suggested_budget = max(current_non_deferred_need / 5.0, 1.0)
    suggested_budget = round(suggested_budget / 100_000) * 100_000

    input1, input2 = st.columns(2)
    baseline_budget = input1.number_input(
        "Baseline Annual Budget ($)",
        min_value=0.0,
        value=float(suggested_budget),
        step=100_000.0,
        format="%.0f",
    )
    constrained_reduction_pct = input2.slider(
        "Constrained Budget Reduction (%)",
        min_value=0,
        max_value=50,
        value=20,
        step=5,
    )

    st.caption(
        "The displayed baseline value is only a starting estimate equal to "
        "one fifth of current unconstrained need. It is not a budget specified "
        "by the project brief and may be replaced with an approved amount."
    )

    if st.button("Run Five-Year Budget Scenarios", type="primary"):
        bci_weights = st.session_state.get(
            "bci_weights",
            {"deck": 0.30, "super": 0.35, "sub": 0.35},
        )
        priority_weights = st.session_state.get(
            "Priority_Weights",
            {"bci": 0.50, "traffic": 0.30, "replacement_cost": 0.20},
        )

        with st.spinner("Running five-year lifecycle and budget scenarios..."):
            detailed_plan, annual_summary = run_budget_scenarios(
                df_current=strategy,
                baseline_annual_budget=float(baseline_budget),
                start_year=current_year,
                bci_weights=bci_weights,
                priority_weights=priority_weights,
                workbook_path=workbook_path,
                constrained_reduction=constrained_reduction_pct / 100.0,
            )

        st.session_state["five_year_plan_detail"] = detailed_plan
        st.session_state["five_year_plan_summary"] = annual_summary
        st.session_state["five_year_plan_settings"] = {
            "baseline_budget": float(baseline_budget),
            "constrained_reduction_pct": constrained_reduction_pct,
        }
        st.success("Five-year scenarios calculated successfully.")

    detailed_plan = st.session_state.get("five_year_plan_detail")
    annual_summary = st.session_state.get("five_year_plan_summary")
    settings = st.session_state.get("five_year_plan_settings")

    if detailed_plan is None or annual_summary is None:
        st.info("Set the annual budget and run the five-year scenarios.")
        return

    if settings:
        st.caption(
            "Displayed results use a baseline annual budget of "
            f"${settings['baseline_budget']:,.0f} and a constrained reduction "
            f"of {settings['constrained_reduction_pct']}%."
        )

    st.markdown("#### Annual Scenario Summary")
    st.dataframe(
        annual_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Annual_Budget": st.column_config.NumberColumn(format="$%,.0f"),
            "Nominal_Spent": st.column_config.NumberColumn(format="$%,.0f"),
            "Discounted_Spent": st.column_config.NumberColumn(format="$%,.0f"),
            "Budget_Remaining": st.column_config.NumberColumn(format="$%,.0f"),
            "Average_BCI_Start": st.column_config.NumberColumn(format="%.2f"),
            "Average_BCI_End": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    bci_chart = annual_summary.pivot(
        index="Calendar_Year",
        columns="Scenario",
        values="Average_BCI_End",
    )
    st.markdown("#### Average End-of-Year BCI")
    st.line_chart(bci_chart)

    st.markdown("#### Programmed Actions Across Five Years")
    action_summary = _build_programmed_action_summary(detailed_plan)
    st.dataframe(
        action_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Programmed_Bridge_Actions": st.column_config.NumberColumn(
                "Programmed Bridge-Actions",
                format="%d",
            ),
            "Nominal_Programmed_Cost": st.column_config.NumberColumn(
                "Nominal Cost",
                format="$%,.0f",
            ),
            "Discounted_Programmed_Cost": st.column_config.NumberColumn(
                "Discounted Cost",
                format="$%,.0f",
            ),
        },
    )

    filter1, filter2 = st.columns(2)
    scenarios = detailed_plan["Scenario"].dropna().unique().tolist()
    years = sorted(detailed_plan["Calendar_Year"].dropna().unique().tolist())
    selected_scenario = filter1.selectbox(
        "Detailed Plan Scenario",
        scenarios,
    )
    selected_year = filter2.selectbox(
        "Detailed Plan Year",
        years,
    )

    filtered = detailed_plan[
        (detailed_plan["Scenario"] == selected_scenario)
        & (detailed_plan["Calendar_Year"] == selected_year)
    ].sort_values(["Priority Rank", "Structure_ID"])

    detail_columns = [
        "Priority Rank",
        "Structure_ID",
        "BCI",
        "Recommended_Treatment_Code",
        "Treatment_Cost",
        "Decision_Status",
        "Programmed_Treatment_Name",
        "Programmed_Cost",
        "BCI_End_of_Year",
    ]
    st.dataframe(
        filtered[detail_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "BCI": st.column_config.NumberColumn("Start BCI", format="%.2f"),
            "Treatment_Cost": st.column_config.NumberColumn(
                "Recommended Cost",
                format="$%,.0f",
            ),
            "Programmed_Cost": st.column_config.NumberColumn(
                "Programmed Cost",
                format="$%,.0f",
            ),
            "BCI_End_of_Year": st.column_config.NumberColumn(
                "End BCI",
                format="%.2f",
            ),
        },
    )

    st.download_button(
        "Download Five-Year Detailed Plan CSV",
        data=detailed_plan.to_csv(index=False).encode("utf-8-sig"),
        file_name="five_year_bridge_investment_plan.csv",
        mime="text/csv",
    )


def _build_programmed_action_summary(
    detailed_plan: pd.DataFrame,
) -> pd.DataFrame:
    catalog = pd.DataFrame(treatment_catalog_as_records())[
        ["Treatment_Code", "Treatment_Name"]
    ].rename(
        columns={
            "Treatment_Code": "Programmed_Treatment_Code",
            "Treatment_Name": "Programmed_Treatment_Name",
        }
    )
    scenarios = pd.DataFrame(
        {"Scenario": detailed_plan["Scenario"].dropna().unique()}
    )
    base = scenarios.merge(catalog, how="cross")

    summary = (
        detailed_plan.groupby(
            [
                "Scenario",
                "Programmed_Treatment_Code",
                "Programmed_Treatment_Name",
            ],
            dropna=False,
        )
        .agg(
            Programmed_Bridge_Actions=("Structure_ID", "count"),
            Nominal_Programmed_Cost=("Programmed_Cost", "sum"),
            Discounted_Programmed_Cost=(
                "Discounted_Programmed_Cost",
                "sum",
            ),
        )
        .reset_index()
    )

    summary = base.merge(
        summary,
        on=[
            "Scenario",
            "Programmed_Treatment_Code",
            "Programmed_Treatment_Name",
        ],
        how="left",
    )
    fill_columns = [
        "Programmed_Bridge_Actions",
        "Nominal_Programmed_Cost",
        "Discounted_Programmed_Cost",
    ]
    summary[fill_columns] = summary[fill_columns].fillna(0)
    summary["Programmed_Bridge_Actions"] = summary[
        "Programmed_Bridge_Actions"
    ].astype(int)

    order_map = {code: index for index, code in enumerate(TREATMENT_ORDER)}
    summary["_order"] = summary["Programmed_Treatment_Code"].map(order_map)
    return (
        summary.sort_values(["Scenario", "_order"])
        .drop(columns=["_order", "Programmed_Treatment_Code"])
        .reset_index(drop=True)
    )
