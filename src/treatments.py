"""Bridge maintenance and rehabilitation treatment models."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, isclose
from typing import Final

from collections.abc import Mapping

import pandas as pd


SQFT_PER_SQM: Final[float] = 10.763910416709722
MAX_TREATED_CONDITION: Final[float] = 99.0


@dataclass(frozen=True, slots=True)
class Treatment:
    """Definition of one bridge maintenance or rehabilitation action."""

    code: str
    name: str
    unit_cost_per_sqm: float

    deck_improvement: float = 0.0
    super_improvement: float = 0.0
    sub_improvement: float = 0.0

    reset_condition_to: float | None = None


TREATMENT_CATALOG: Final[dict[str, Treatment]] = {
    "deferred": Treatment(
        code="deferred",
        name="Deferred Action",
        unit_cost_per_sqm=0.0,
    ),
    "preventive_maintenance": Treatment(
        code="preventive_maintenance",
        name="Preventive Maintenance",
        unit_cost_per_sqm=140.0 * SQFT_PER_SQM,
        deck_improvement=11.0,
        super_improvement=8.0,
        sub_improvement=8.0,
    ),
    "regular_rehabilitation": Treatment(
        code="regular_rehabilitation",
        name="Regular Rehabilitation",
        unit_cost_per_sqm=240.0 * SQFT_PER_SQM,
        deck_improvement=45.0,
        super_improvement=27.0,
        sub_improvement=23.0,
    ),
    "heavy_rehabilitation": Treatment(
        code="heavy_rehabilitation",
        name="Heavy Rehabilitation",
        unit_cost_per_sqm=380.0 * SQFT_PER_SQM,
        deck_improvement=70.0,
        super_improvement=62.0,
        sub_improvement=49.0,
    ),
    "bridge_replacement": Treatment(
        code="bridge_replacement",
        name="Bridge Replacement",
        unit_cost_per_sqm=800.0 * SQFT_PER_SQM,
        reset_condition_to=99.0,
    ),
}

def get_treatment(treatment_code: str) -> Treatment:
    """Return a treatment definition using its catalogue code."""

    normalized_code = str(treatment_code).strip().lower()

    try:
        return TREATMENT_CATALOG[normalized_code]

    except KeyError as exc:
        valid_codes = ", ".join(TREATMENT_CATALOG)

        raise ValueError(
            f"Unknown treatment code: {treatment_code!r}. "
            f"Valid treatment codes are: {valid_codes}."
        ) from exc

def calculate_deck_area_sqm(
    nominal_bridge_length_m: float,
    total_clear_roadway_m: float,
) -> float:
    """Calculate bridge deck area in square metres."""

    length_m = _validate_positive_number(
        nominal_bridge_length_m,
        "Nominal bridge length",
    )

    roadway_width_m = _validate_positive_number(
        total_clear_roadway_m,
        "Total clear roadway",
    )

    return length_m * roadway_width_m

def calculate_treatment_cost(
    treatment_code: str,
    nominal_bridge_length_m: float,
    total_clear_roadway_m: float,
) -> float:
    """Calculate treatment cost using square-metre bridge dimensions."""

    treatment = get_treatment(treatment_code)

    if treatment.unit_cost_per_sqm == 0:
        return 0.0

    deck_area_sqm = calculate_deck_area_sqm(
        nominal_bridge_length_m=nominal_bridge_length_m,
        total_clear_roadway_m=total_clear_roadway_m,
    )

    return deck_area_sqm * treatment.unit_cost_per_sqm

def apply_treatment(
    treatment_code: str,
    deck_condition: float,
    super_condition: float,
    sub_condition: float,
) -> dict[str, float]:
    """Calculate component conditions immediately after treatment."""

    treatment = get_treatment(treatment_code)

    deck_before = _validate_condition_rating(
        deck_condition,
        "Deck condition",
    )

    super_before = _validate_condition_rating(
        super_condition,
        "Superstructure condition",
    )

    sub_before = _validate_condition_rating(
        sub_condition,
        "Substructure condition",
    )

    if treatment.reset_condition_to is not None:
        reset_value = float(treatment.reset_condition_to)

        return {
            "Deck_After_Treatment": reset_value,
            "Super_After_Treatment": reset_value,
            "Sub_After_Treatment": reset_value,
        }

    if treatment.code == "deferred":
        return {
            "Deck_After_Treatment": deck_before,
            "Super_After_Treatment": super_before,
            "Sub_After_Treatment": sub_before,
        }

    return {
        "Deck_After_Treatment": min(
            MAX_TREATED_CONDITION,
            deck_before + treatment.deck_improvement,
        ),
        "Super_After_Treatment": min(
            MAX_TREATED_CONDITION,
            super_before + treatment.super_improvement,
        ),
        "Sub_After_Treatment": min(
            MAX_TREATED_CONDITION,
            sub_before + treatment.sub_improvement,
        ),
    }


def evaluate_treatment(
    treatment_code: str,
    nominal_bridge_length_m: float,
    total_clear_roadway_m: float,
    deck_condition: float,
    super_condition: float,
    sub_condition: float,
) -> dict[str, str | float]:
    """Return the cost and component effects of one treatment option."""

    treatment = get_treatment(treatment_code)

    deck_area_sqm = calculate_deck_area_sqm(
        nominal_bridge_length_m=nominal_bridge_length_m,
        total_clear_roadway_m=total_clear_roadway_m,
    )

    treatment_cost = calculate_treatment_cost(
        treatment_code=treatment_code,
        nominal_bridge_length_m=nominal_bridge_length_m,
        total_clear_roadway_m=total_clear_roadway_m,
    )

    outcome = apply_treatment(
        treatment_code=treatment_code,
        deck_condition=deck_condition,
        super_condition=super_condition,
        sub_condition=sub_condition,
    )

    return {
        "Treatment_Code": treatment.code,
        "Treatment_Name": treatment.name,
        "Unit_Cost_per_m2": treatment.unit_cost_per_sqm,
        "Deck_Area_m2": deck_area_sqm,
        "Treatment_Cost": treatment_cost,
        **outcome,
    }

def evaluate_recommended_treatments_for_network(
    df: pd.DataFrame,
    bci_weights: Mapping[str, float],
) -> pd.DataFrame:
    """Calculate treatment cost and post-treatment condition for each bridge."""

    required_columns = [
        "Recommended_Treatment_Code",
        "Nominal_Bridge_Ln",
        "Total_Clear_Roadway",
        "current_Cond_Rat_Deck",
        "current_Cond_Rat_Super",
        "current_Cond_Rat_Sub",
        "BCI",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            "Treatment evaluation requires these columns: "
            + ", ".join(missing_columns)
        )

    validated_weights = _validate_bci_weights(
        bci_weights
    )

    result = df.copy()

    treatment_results = result.apply(
        lambda row: evaluate_treatment(
            treatment_code=row["Recommended_Treatment_Code"],
            nominal_bridge_length_m=row["Nominal_Bridge_Ln"],
            total_clear_roadway_m=row["Total_Clear_Roadway"],
            deck_condition=row["current_Cond_Rat_Deck"],
            super_condition=row["current_Cond_Rat_Super"],
            sub_condition=row["current_Cond_Rat_Sub"],
        ),
        axis=1,
        result_type="expand",
    )

    duplicate_columns = [
        column
        for column in treatment_results.columns
        if column in result.columns
    ]

    if duplicate_columns:
        result = result.drop(
            columns=duplicate_columns
        )

    result = pd.concat(
        [
            result,
            treatment_results,
        ],
        axis=1,
    )

    result["BCI_After_Treatment"] = (
        validated_weights["deck"]
        * result["Deck_After_Treatment"]
        + validated_weights["super"]
        * result["Super_After_Treatment"]
        + validated_weights["sub"]
        * result["Sub_After_Treatment"]
    )

    result["BCI_Improvement"] = (
        result["BCI_After_Treatment"]
        - result["BCI"]
    ).clip(lower=0.0)

    result["Treatment_Cost"] = pd.to_numeric(
        result["Treatment_Cost"],
        errors="coerce",
    )

    result["Treatment_Cost_per_BCI_Point"] = (
        result["Treatment_Cost"]
        / result["BCI_Improvement"].where(
            result["BCI_Improvement"] > 0
        )
    )

    return result

def treatment_catalog_as_records() -> list[dict[str, str | float | None]]:
    """Return the treatment catalogue in a table-friendly format."""

    return [
        {
            "Treatment_Code": treatment.code,
            "Treatment_Name": treatment.name,
            "Unit_Cost_per_m2": treatment.unit_cost_per_sqm,
            "Deck_Improvement": treatment.deck_improvement,
            "Super_Improvement": treatment.super_improvement,
            "Sub_Improvement": treatment.sub_improvement,
            "Reset_Condition_To": treatment.reset_condition_to,
        }
        for treatment in TREATMENT_CATALOG.values()
    ]


def _validate_positive_number(
    value: float,
    label: str,
) -> float:
    """Return a finite positive numeric value."""

    try:
        numeric_value = float(value)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{label} must be numeric; received {value!r}."
        ) from exc

    if not isfinite(numeric_value):
        raise ValueError(
            f"{label} must be finite; received {numeric_value!r}."
        )

    if numeric_value <= 0:
        raise ValueError(
            f"{label} must be greater than zero; "
            f"received {numeric_value!r}."
        )

    return numeric_value


def _validate_condition_rating(
    value: float,
    label: str,
) -> float:
    """Validate a bridge component condition rating."""

    try:
        numeric_value = float(value)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{label} must be numeric; received {value!r}."
        ) from exc

    if not isfinite(numeric_value):
        raise ValueError(
            f"{label} must be finite; received {numeric_value!r}."
        )

    if not 0 <= numeric_value <= 100:
        raise ValueError(
            f"{label} must be between 0 and 100; "
            f"received {numeric_value!r}."
        )

    return numeric_value

def _validate_bci_weights(
    weights: Mapping[str, float],
) -> dict[str, float]:
    """Validate BCI weights used for post-treatment BCI calculation."""

    required_keys = [
        "deck",
        "super",
        "sub",
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in weights
    ]

    if missing_keys:
        raise ValueError(
            "BCI weights are missing these keys: "
            + ", ".join(missing_keys)
        )

    validated_weights: dict[str, float] = {}

    for key in required_keys:
        try:
            numeric_value = float(weights[key])

        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"BCI weight {key!r} must be numeric."
            ) from exc

        if not isfinite(numeric_value):
            raise ValueError(
                f"BCI weight {key!r} must be finite."
            )

        if numeric_value < 0:
            raise ValueError(
                f"BCI weight {key!r} cannot be negative."
            )

        validated_weights[key] = numeric_value

    total_weight = sum(
        validated_weights.values()
    )

    if not isclose(
        total_weight,
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "BCI weights must sum to 1.00; "
            f"received {total_weight:.4f}."
        )

    return validated_weights