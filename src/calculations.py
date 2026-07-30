"""Bridge condition, BCI, and investment-priority calculations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from src.deterioration import (
    DEFAULT_EXCEL_FILE_PATH,
    DeteriorationMappingError,
    calculate_decay,
    load_deterioration_rates,
)


def calculate_bci(
    df: pd.DataFrame,
    w_deck: float,
    w_super: float,
    w_sub: float,
) -> pd.DataFrame:
    """Return a copy of the data with a weighted Bridge Condition Index."""

    _validate_weights(
        {"deck": w_deck, "super": w_super, "sub": w_sub},
        "BCI",
    )

    df_temp = df.copy()
    df_temp["BCI"] = (
        w_deck * df_temp["current_Cond_Rat_Deck"]
        + w_super * df_temp["current_Cond_Rat_Super"]
        + w_sub * df_temp["current_Cond_Rat_Sub"]
    )
    return df_temp


def normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize valid values to 0-100 without division by zero."""

    numeric_series = pd.to_numeric(series, errors="coerce")
    normalized = pd.Series(
        np.nan,
        index=numeric_series.index,
        dtype=float,
    )

    valid_mask = numeric_series.notna()
    valid_values = numeric_series.loc[valid_mask]

    if valid_values.empty:
        return normalized

    min_value = valid_values.min()
    max_value = valid_values.max()

    if np.isclose(max_value, min_value):
        normalized.loc[valid_mask] = 0.0
        return normalized

    normalized.loc[valid_mask] = (
        (valid_values - min_value)
        / (max_value - min_value)
        * 100
    )
    return normalized


def run_all_calculations(
    df: pd.DataFrame,
    current_year: int,
    workbook_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, float | int],
]:
    """Run live deterioration, BCI, priority, and KPI calculations.

    Exact deterioration rates are loaded from the workbook. The original
    bridge category is preserved. Deterioration groups are selected from
    the span-type structural family. Combined spans use the maximum
    component deterioration rate in each simulated year.
    """

    df_processed = df.copy()

    invalid_mapping_mask = (
        df_processed.get(
            "Deterioration_Mapping_Status",
            pd.Series("Direct", index=df_processed.index),
        )
        == "Invalid"
    )
    if invalid_mapping_mask.any():
        invalid_ids = (
            df_processed.loc[invalid_mapping_mask, "Structure_ID"]
            .astype(str)
            .tolist()
        )
        raise DeteriorationMappingError(
            "Calculations stopped because these records have invalid "
            "deterioration mappings: " + ", ".join(invalid_ids)
        )

    rate_table = load_deterioration_rates(workbook_path)

    # Current component condition ratings.
    df_processed["current_Cond_Rat_Deck"] = df_processed.apply(
        lambda row: calculate_decay(
            initial_rating=row["Cond_Rat_Deck"],
            bridge_category=row["Bridge_Cat"],
            span_type=row["Unique_Span_Type"],
            years=row["Years_Passed"],
            rate_table=rate_table,
        ),
        axis=1,
    )

    df_processed["current_Cond_Rat_Super"] = df_processed.apply(
        lambda row: calculate_decay(
            initial_rating=row["Cond_Rat_Super"],
            bridge_category=row["Bridge_Cat"],
            span_type=row["Unique_Span_Type"],
            years=row["Years_Passed"],
            rate_table=rate_table,
        ),
        axis=1,
    )

    df_processed["current_Cond_Rat_Sub"] = df_processed.apply(
        lambda row: calculate_decay(
            initial_rating=row["Cond_Rat_Sub"],
            bridge_category=row["Bridge_Cat"],
            span_type=row["Unique_Span_Type"],
            years=row["Years_Passed"],
            rate_table=rate_table,
        ),
        axis=1,
    )

    # BCI calculation.
    bci_weights = st.session_state.get(
        "bci_weights",
        {"deck": 0.30, "super": 0.35, "sub": 0.35},
    )
    bci_weights = {
        "deck": float(bci_weights.get("deck", 0.30)),
        "super": float(bci_weights.get("super", 0.35)),
        "sub": float(bci_weights.get("sub", 0.35)),
    }
    
    df_processed = calculate_bci(
        df=df_processed,
        w_deck=bci_weights["deck"],
        w_super=bci_weights["super"],
        w_sub=bci_weights["sub"],
    )

    df_processed["Age"] = current_year - df_processed["First_Year_In_Service"]

    # Priority score calculation.
    priority_weights = st.session_state.get(
        "Priority_Weights",
        {"bci": 0.50, "traffic": 0.30, "replacement_cost": 0.20},
    )
    priority_weights = {
        "bci": float(priority_weights.get("bci", 0.50)),
        "traffic": float(priority_weights.get("traffic", 0.30)),
        "replacement_cost": float(
            priority_weights.get("replacement_cost", 0.20)
        ),
    }
    _validate_weights(priority_weights, "Prioritization")

    df_processed["Condition_Score"] = normalize(100 - df_processed["BCI"])
    df_processed["Traffic_Score"] = normalize(df_processed["Traffic_Volume"])
    df_processed["Cost_Score"] = normalize(df_processed["Replacement_Cost"])
    df_processed["Priority Score"] = (
        priority_weights["bci"] * df_processed["Condition_Score"]
        + priority_weights["traffic"] * df_processed["Traffic_Score"]
        + priority_weights["replacement_cost"] * df_processed["Cost_Score"]
    )

    df_processed["Priority Rank"] = (
        df_processed["Priority Score"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype("Int64")
    )

    df_processed["Bridge_condition_Cat"] = pd.cut(
        df_processed["BCI"],
        bins=[
            -np.inf,
            50,
            70,
            np.inf,
        ],
        labels=[
            "Poor",
            "Fair",
            "Good",
        ],
        right=False,
    ).astype("string")

    df_processed["Bridge_condition_Cat"] = pd.cut(
        df_processed["BCI"],
        bins=[
            -np.inf,
            50,
            70,
            np.inf,
        ],
        labels=[
            "Poor",
            "Fair",
            "Good",
        ],
        right=False,
    ).astype("string")

    # Ranked subsets are created only after all required columns exist.
    lowest_bci = df_processed.nsmallest(20, "BCI").copy()
    top10 = (
        df_processed
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
        .head(10)
        .copy()
    )

    summary = pd.DataFrame(
        {
            "Type": df_processed.dtypes,
            "Missing": df_processed.isna().sum(),
            "Missing %": (
                df_processed.isna().sum() / len(df_processed) * 100
            ).round(2),
            "Unique": df_processed.nunique(),
        }
    )

    bridge_count = int(df_processed.shape[0])
    kpi_card_info: dict[str, float | int] = {
        "totalBridgeCount": bridge_count,
        "totalCost": float(df_processed["Replacement_Cost"].sum()),
        "averageAge": float(df_processed["Age"].mean()),
        "averageConditionRating": float(df_processed["BCI"].mean()),
        "totalDailyTraffic": float(df_processed["Traffic_Volume"].sum()),
    }

    return df_processed, summary, top10, lowest_bci, kpi_card_info


def _validate_weights(weights: dict[str, float], label: str) -> None:
    """Reject malformed or non-normalized analysis weights."""

    values = np.array(list(weights.values()), dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{label} weights must be finite numbers.")
    if (values < 0).any():
        raise ValueError(f"{label} weights cannot be negative.")
    if not np.isclose(values.sum(), 1.0):
        raise ValueError(
            f"{label} weights must sum to 1.00; received {values.sum():.4f}."
        )