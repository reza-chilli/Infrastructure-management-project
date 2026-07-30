"""Configurable bridge treatment recommendation policy."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import pandas as pd


@dataclass(frozen=True, slots=True)
class TreatmentPolicy:
    """Thresholds used to recommend bridge interventions.

    These thresholds are project modelling assumptions and should remain
    configurable until formally approved.
    """

    replacement_bci: float = 35.0
    replacement_component: float = 30.0
    replacement_component_count: int = 2

    heavy_rehab_bci: float = 50.0
    heavy_rehab_component: float = 40.0

    regular_rehab_bci: float = 70.0
    regular_rehab_component: float = 60.0

    preventive_bci: float = 85.0
    preventive_component: float = 75.0


DEFAULT_TREATMENT_POLICY = TreatmentPolicy()


def recommend_treatment(
    bci: float,
    deck_condition: float,
    super_condition: float,
    sub_condition: float,
    policy: TreatmentPolicy = DEFAULT_TREATMENT_POLICY,
) -> dict[str, str | float | int]:
    """Recommend an intervention using BCI and component conditions."""

    bci_value = _validate_condition(bci, "BCI")
    components = {
        "Deck": _validate_condition(deck_condition, "Deck condition"),
        "Superstructure": _validate_condition(
            super_condition,
            "Superstructure condition",
        ),
        "Substructure": _validate_condition(
            sub_condition,
            "Substructure condition",
        ),
    }

    minimum_component_name = min(
        components,
        key=components.get,
    )
    minimum_component_value = components[minimum_component_name]

    replacement_component_count = sum(
        value < policy.replacement_component
        for value in components.values()
    )

    if (
        bci_value < policy.replacement_bci
        or replacement_component_count
        >= policy.replacement_component_count
    ):
        treatment_code = "bridge_replacement"
        reason = (
            "Very poor network condition or multiple critically "
            "deteriorated components."
        )

    elif (
        bci_value < policy.heavy_rehab_bci
        or minimum_component_value
        < policy.heavy_rehab_component
    ):
        treatment_code = "heavy_rehabilitation"
        reason = (
            "Poor overall condition or at least one severely "
            "deteriorated component."
        )

    elif (
        bci_value < policy.regular_rehab_bci
        or minimum_component_value
        < policy.regular_rehab_component
    ):
        treatment_code = "regular_rehabilitation"
        reason = (
            "Fair overall condition or a component requiring "
            "substantial rehabilitation."
        )

    elif (
        bci_value < policy.preventive_bci
        or minimum_component_value
        < policy.preventive_component
    ):
        treatment_code = "preventive_maintenance"
        reason = (
            "Generally serviceable condition with emerging "
            "maintenance needs."
        )

    else:
        treatment_code = "deferred"
        reason = (
            "Bridge and component conditions are currently above "
            "the intervention thresholds."
        )

    return {
        "Recommended_Treatment_Code": treatment_code,
        "Recommendation_Reason": reason,
        "Minimum_Component": minimum_component_name,
        "Minimum_Component_Condition": minimum_component_value,
        "Critical_Component_Count": replacement_component_count,
    }


def recommend_treatments_for_network(
    df: pd.DataFrame,
    policy: TreatmentPolicy = DEFAULT_TREATMENT_POLICY,
) -> pd.DataFrame:
    """Add treatment recommendations to a processed bridge dataset."""

    required_columns = [
        "BCI",
        "current_Cond_Rat_Deck",
        "current_Cond_Rat_Super",
        "current_Cond_Rat_Sub",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            "Treatment recommendations require these columns: "
            + ", ".join(missing_columns)
        )

    result = df.copy()

    recommendations = result.apply(
        lambda row: recommend_treatment(
            bci=row["BCI"],
            deck_condition=row["current_Cond_Rat_Deck"],
            super_condition=row["current_Cond_Rat_Super"],
            sub_condition=row["current_Cond_Rat_Sub"],
            policy=policy,
        ),
        axis=1,
        result_type="expand",
    )

    return pd.concat(
        [
            result,
            recommendations,
        ],
        axis=1,
    )


def treatment_policy_as_records(
    policy: TreatmentPolicy = DEFAULT_TREATMENT_POLICY,
) -> list[dict[str, str | float | int]]:
    """Return the active decision rules in table-friendly form."""

    return [
        {
            "Treatment": "Bridge Replacement",
            "BCI Trigger": f"< {policy.replacement_bci}",
            "Component Trigger": (
                f"{policy.replacement_component_count} or more "
                f"components < {policy.replacement_component}"
            ),
        },
        {
            "Treatment": "Heavy Rehabilitation",
            "BCI Trigger": f"< {policy.heavy_rehab_bci}",
            "Component Trigger": (
                f"Any component < {policy.heavy_rehab_component}"
            ),
        },
        {
            "Treatment": "Regular Rehabilitation",
            "BCI Trigger": f"< {policy.regular_rehab_bci}",
            "Component Trigger": (
                f"Any component < {policy.regular_rehab_component}"
            ),
        },
        {
            "Treatment": "Preventive Maintenance",
            "BCI Trigger": f"< {policy.preventive_bci}",
            "Component Trigger": (
                f"Any component < {policy.preventive_component}"
            ),
        },
        {
            "Treatment": "Deferred Action",
            "BCI Trigger": (
                f">= {policy.preventive_bci}"
            ),
            "Component Trigger": (
                f"All components >= {policy.preventive_component}"
            ),
        },
    ]


def _validate_condition(
    value: float,
    label: str,
) -> float:
    """Validate a BCI or component condition value."""

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