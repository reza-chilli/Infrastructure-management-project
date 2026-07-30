"""Transparent five-year bridge lifecycle and budget planning."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import numpy as np
import pandas as pd

from src.deterioration import (
    DEFAULT_EXCEL_FILE_PATH,
    calculate_decay,
    load_deterioration_rates,
)
from src.treatment_policy import recommend_treatments_for_network
from src.treatments import (
    evaluate_recommended_treatments_for_network,
    get_treatment,
)


DEFAULT_HORIZON_YEARS = 5
DEFAULT_TRAFFIC_GROWTH_RATE = 0.06
DEFAULT_DISCOUNT_RATE = 0.05
DEFAULT_CONSTRAINED_REDUCTION = 0.20

CONDITION_COLUMNS = [
    "current_Cond_Rat_Deck",
    "current_Cond_Rat_Super",
    "current_Cond_Rat_Sub",
]

YEAR_DERIVED_COLUMNS = [
    "BCI",
    "Age",
    "Condition_Score",
    "Traffic_Score",
    "Cost_Score",
    "Priority Score",
    "Priority Rank",
    "Bridge_condition_Cat",
    "Recommended_Treatment_Code",
    "Recommendation_Reason",
    "Minimum_Component",
    "Minimum_Component_Condition",
    "Critical_Component_Count",
    "Treatment_Code",
    "Treatment_Name",
    "Unit_Cost_per_m2",
    "Deck_Area_m2",
    "Treatment_Cost",
    "Deck_After_Treatment",
    "Super_After_Treatment",
    "Sub_After_Treatment",
    "BCI_After_Treatment",
    "BCI_Improvement",
    "Treatment_Cost_per_BCI_Point",
    "Funded",
    "Decision_Status",
    "Programmed_Treatment_Code",
    "Programmed_Treatment_Name",
    "Programmed_Cost",
    "Discounted_Programmed_Cost",
    "Deck_End_of_Year",
    "Super_End_of_Year",
    "Sub_End_of_Year",
    "BCI_End_of_Year",
    "End_Condition_Category",
]


def simulate_five_year_plan(
    df_current: pd.DataFrame,
    annual_budget: float,
    start_year: int,
    bci_weights: Mapping[str, float],
    priority_weights: Mapping[str, float],
    workbook_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
    scenario_name: str = "Baseline Budget",
    horizon_years: int = DEFAULT_HORIZON_YEARS,
    traffic_growth_rate: float = DEFAULT_TRAFFIC_GROWTH_RATE,
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate annual deterioration, prioritization, funding, and treatment."""

    _validate_inputs(
        df_current=df_current,
        annual_budget=annual_budget,
        horizon_years=horizon_years,
        traffic_growth_rate=traffic_growth_rate,
        discount_rate=discount_rate,
    )
    bci_weights = _validate_weights(bci_weights, "BCI")
    priority_weights = _validate_weights(priority_weights, "Prioritization")
    rate_table = load_deterioration_rates(workbook_path)

    state = df_current.copy()
    plan_records: list[pd.DataFrame] = []
    annual_records: list[dict[str, float | int | str]] = []

    for plan_year in range(1, horizon_years + 1):
        calendar_year = int(start_year) + plan_year - 1

        state = state.drop(
            columns=[
                column
                for column in YEAR_DERIVED_COLUMNS
                if column in state.columns
            ],
            errors="ignore",
        )

        if plan_year > 1:
            state = _deteriorate_one_year(
                state,
                rate_table=rate_table,
            )
            state["Traffic_Volume"] = (
                pd.to_numeric(state["Traffic_Volume"], errors="coerce")
                * (1.0 + traffic_growth_rate)
            )

        state = _calculate_annual_metrics(
            state,
            calendar_year=calendar_year,
            bci_weights=bci_weights,
            priority_weights=priority_weights,
        )
        state = recommend_treatments_for_network(state)
        state = evaluate_recommended_treatments_for_network(
            df=state,
            bci_weights=bci_weights,
        )
        state, budget_remaining = _allocate_budget(
            state,
            annual_budget=float(annual_budget),
            discount_rate=discount_rate,
            plan_year=plan_year,
            bci_weights=bci_weights,
        )

        annual_output = _build_annual_output(
            state,
            scenario_name=scenario_name,
            plan_year=plan_year,
            calendar_year=calendar_year,
            annual_budget=float(annual_budget),
            budget_remaining=budget_remaining,
        )
        plan_records.append(annual_output)

        annual_records.append(
            {
                "Scenario": scenario_name,
                "Plan_Year": plan_year,
                "Calendar_Year": calendar_year,
                "Annual_Budget": float(annual_budget),
                "Nominal_Spent": float(state["Programmed_Cost"].sum()),
                "Discounted_Spent": float(
                    state["Discounted_Programmed_Cost"].sum()
                ),
                "Budget_Remaining": float(budget_remaining),
                "Funded_Bridges": int(state["Funded"].sum()),
                "Deferred_Due_to_Budget": int(
                    (state["Decision_Status"] == "Deferred Due to Budget").sum()
                ),
                "No_Action_Needed": int(
                    (state["Decision_Status"] == "No Action Needed").sum()
                ),
                "Average_BCI_Start": float(state["BCI"].mean()),
                "Average_BCI_End": float(state["BCI_End_of_Year"].mean()),
                "Poor_Bridges_Start": int(
                    (state["Bridge_condition_Cat"] == "Poor").sum()
                ),
                "Poor_Bridges_End": int(
                    (state["End_Condition_Category"] == "Poor").sum()
                ),
            }
        )

        state["current_Cond_Rat_Deck"] = state["Deck_End_of_Year"]
        state["current_Cond_Rat_Super"] = state["Super_End_of_Year"]
        state["current_Cond_Rat_Sub"] = state["Sub_End_of_Year"]

    detailed_plan = pd.concat(plan_records, ignore_index=True)
    annual_summary = pd.DataFrame(annual_records)
    return detailed_plan, annual_summary


def run_budget_scenarios(
    df_current: pd.DataFrame,
    baseline_annual_budget: float,
    start_year: int,
    bci_weights: Mapping[str, float],
    priority_weights: Mapping[str, float],
    workbook_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
    constrained_reduction: float = DEFAULT_CONSTRAINED_REDUCTION,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline and constrained five-year budget scenarios."""

    if not 0 <= constrained_reduction < 1:
        raise ValueError("Constrained budget reduction must be from 0 to less than 1.")

    constrained_budget = baseline_annual_budget * (1.0 - constrained_reduction)

    baseline_detail, baseline_summary = simulate_five_year_plan(
        df_current=df_current,
        annual_budget=baseline_annual_budget,
        start_year=start_year,
        bci_weights=bci_weights,
        priority_weights=priority_weights,
        workbook_path=workbook_path,
        scenario_name="Baseline Budget",
    )
    constrained_detail, constrained_summary = simulate_five_year_plan(
        df_current=df_current,
        annual_budget=constrained_budget,
        start_year=start_year,
        bci_weights=bci_weights,
        priority_weights=priority_weights,
        workbook_path=workbook_path,
        scenario_name="Constrained Budget",
    )

    return (
        pd.concat([baseline_detail, constrained_detail], ignore_index=True),
        pd.concat([baseline_summary, constrained_summary], ignore_index=True),
    )


def _deteriorate_one_year(
    df: pd.DataFrame,
    rate_table,
) -> pd.DataFrame:
    result = df.copy()

    for condition_column in CONDITION_COLUMNS:
        result[condition_column] = result.apply(
            lambda row: calculate_decay(
                initial_rating=row[condition_column],
                bridge_category=row["Bridge_Cat"],
                span_type=row["Unique_Span_Type"],
                years=1,
                rate_table=rate_table,
            ),
            axis=1,
        )

    return result


def _calculate_annual_metrics(
    df: pd.DataFrame,
    calendar_year: int,
    bci_weights: Mapping[str, float],
    priority_weights: Mapping[str, float],
) -> pd.DataFrame:
    result = df.copy()

    result["BCI"] = (
        bci_weights["deck"] * result["current_Cond_Rat_Deck"]
        + bci_weights["super"] * result["current_Cond_Rat_Super"]
        + bci_weights["sub"] * result["current_Cond_Rat_Sub"]
    )
    result["Age"] = calendar_year - result["First_Year_In_Service"]

    result["Condition_Score"] = _normalize(100.0 - result["BCI"])
    result["Traffic_Score"] = _normalize(result["Traffic_Volume"])
    result["Cost_Score"] = _normalize(result["Replacement_Cost"])
    result["Priority Score"] = (
        priority_weights["bci"] * result["Condition_Score"]
        + priority_weights["traffic"] * result["Traffic_Score"]
        + priority_weights["replacement_cost"] * result["Cost_Score"]
    )
    result["Priority Rank"] = (
        result["Priority Score"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    result["Bridge_condition_Cat"] = _condition_category(result["BCI"])
    return result


def _allocate_budget(
    df: pd.DataFrame,
    annual_budget: float,
    discount_rate: float,
    plan_year: int,
    bci_weights: Mapping[str, float],
) -> tuple[pd.DataFrame, float]:
    result = df.copy()
    remaining_budget = float(annual_budget)
    funded_indices: list[object] = []

    candidates = result.sort_values(
        by=["Priority Rank", "Structure_ID"],
        ascending=[True, True],
    )

    for index, row in candidates.iterrows():
        if row["Recommended_Treatment_Code"] == "deferred":
            continue

        treatment_cost = float(row["Treatment_Cost"])
        if treatment_cost <= remaining_budget + 1e-9:
            funded_indices.append(index)
            remaining_budget -= treatment_cost

    result["Funded"] = result.index.isin(funded_indices)
    result["Programmed_Treatment_Code"] = np.where(
        result["Funded"],
        result["Recommended_Treatment_Code"],
        "deferred",
    )
    result["Programmed_Treatment_Name"] = result[
        "Programmed_Treatment_Code"
    ].map(lambda code: get_treatment(code).name)
    result["Programmed_Cost"] = np.where(
        result["Funded"],
        result["Treatment_Cost"],
        0.0,
    )
    result["Discounted_Programmed_Cost"] = (
        result["Programmed_Cost"]
        / ((1.0 + discount_rate) ** (plan_year - 1))
    )

    result["Decision_Status"] = "No Action Needed"
    result.loc[
        result["Recommended_Treatment_Code"] != "deferred",
        "Decision_Status",
    ] = "Deferred Due to Budget"
    result.loc[result["Funded"], "Decision_Status"] = "Funded"

    result["Deck_End_of_Year"] = np.where(
        result["Funded"],
        result["Deck_After_Treatment"],
        result["current_Cond_Rat_Deck"],
    )
    result["Super_End_of_Year"] = np.where(
        result["Funded"],
        result["Super_After_Treatment"],
        result["current_Cond_Rat_Super"],
    )
    result["Sub_End_of_Year"] = np.where(
        result["Funded"],
        result["Sub_After_Treatment"],
        result["current_Cond_Rat_Sub"],
    )
    result["BCI_End_of_Year"] = (
        bci_weights["deck"] * result["Deck_End_of_Year"]
        + bci_weights["super"] * result["Super_End_of_Year"]
        + bci_weights["sub"] * result["Sub_End_of_Year"]
    )
    result["End_Condition_Category"] = _condition_category(
        result["BCI_End_of_Year"]
    )

    return result, max(0.0, remaining_budget)


def _build_annual_output(
    df: pd.DataFrame,
    scenario_name: str,
    plan_year: int,
    calendar_year: int,
    annual_budget: float,
    budget_remaining: float,
) -> pd.DataFrame:
    result = df.copy()
    result.insert(0, "Scenario", scenario_name)
    result.insert(1, "Plan_Year", plan_year)
    result.insert(2, "Calendar_Year", calendar_year)
    result["Annual_Budget"] = annual_budget
    result["Budget_Remaining"] = budget_remaining

    output_columns = [
        "Scenario",
        "Plan_Year",
        "Calendar_Year",
        "Structure_ID",
        "Priority Rank",
        "Priority Score",
        "Traffic_Volume",
        "BCI",
        "Bridge_condition_Cat",
        "current_Cond_Rat_Deck",
        "current_Cond_Rat_Super",
        "current_Cond_Rat_Sub",
        "Recommended_Treatment_Code",
        "Treatment_Name",
        "Recommendation_Reason",
        "Treatment_Cost",
        "Funded",
        "Decision_Status",
        "Programmed_Treatment_Code",
        "Programmed_Treatment_Name",
        "Programmed_Cost",
        "Discounted_Programmed_Cost",
        "Deck_End_of_Year",
        "Super_End_of_Year",
        "Sub_End_of_Year",
        "BCI_End_of_Year",
        "End_Condition_Category",
        "Annual_Budget",
        "Budget_Remaining",
    ]
    return result[output_columns].copy()


def _normalize(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    output = pd.Series(np.nan, index=numeric.index, dtype=float)

    if valid.empty:
        return output
    if np.isclose(valid.max(), valid.min()):
        output.loc[numeric.notna()] = 0.0
        return output

    output.loc[numeric.notna()] = (
        (numeric.loc[numeric.notna()] - valid.min())
        / (valid.max() - valid.min())
        * 100.0
    )
    return output


def _condition_category(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=[-np.inf, 50.0, 70.0, np.inf],
        labels=["Poor", "Fair", "Good"],
        right=False,
    ).astype("string")


def _validate_weights(
    weights: Mapping[str, float],
    label: str,
) -> dict[str, float]:
    required = (
        ("deck", "super", "sub")
        if label == "BCI"
        else ("bci", "traffic", "replacement_cost")
    )
    missing = [key for key in required if key not in weights]
    if missing:
        raise ValueError(f"{label} weights are missing: {', '.join(missing)}")

    validated = {key: float(weights[key]) for key in required}
    values = np.array(list(validated.values()), dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError(f"{label} weights must be finite and non-negative.")
    if not np.isclose(values.sum(), 1.0):
        raise ValueError(
            f"{label} weights must sum to 1.00; received {values.sum():.4f}."
        )
    return validated


def _validate_inputs(
    df_current: pd.DataFrame,
    annual_budget: float,
    horizon_years: int,
    traffic_growth_rate: float,
    discount_rate: float,
) -> None:
    required_columns = {
        "Structure_ID",
        "Bridge_Cat",
        "Unique_Span_Type",
        "First_Year_In_Service",
        "Replacement_Cost",
        "Traffic_Volume",
        "Nominal_Bridge_Ln",
        "Total_Clear_Roadway",
        *CONDITION_COLUMNS,
    }
    missing = sorted(required_columns - set(df_current.columns))
    if missing:
        raise KeyError(
            "Five-year planning requires these columns: " + ", ".join(missing)
        )
    if not np.isfinite(float(annual_budget)) or float(annual_budget) < 0:
        raise ValueError("Annual budget must be a finite non-negative number.")
    if not isinstance(horizon_years, int) or horizon_years <= 0:
        raise ValueError("Planning horizon must be a positive whole number.")
    if not 0 <= float(traffic_growth_rate) < 1:
        raise ValueError("Traffic growth rate must be from 0 to less than 1.")
    if not 0 <= float(discount_rate) < 1:
        raise ValueError("Discount rate must be from 0 to less than 1.")
