"""Deterioration-rate loading, span mapping, and condition decay.

The source bridge data is never overwritten by this module. Instead, each
record is resolved to one or more deterioration model groups. Direct records
use their approved group; category/span mismatches are resolved from the span
code; combined spans use the maximum applicable component rate in each year.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


DEFAULT_EXCEL_FILE_PATH = "ToR Structures_Data_Updated- bahman 1405.xlsx"
DETERIORATION_RATES_SHEET = "Bridge Deterioration Rates"

# Model-group names must match the first column of the workbook rate sheet.
GROUP_STANDARD_OTHER = "Other"
GROUP_PRESTRESSED_CONCRETE = "Prestressed Girder -Concrete"
GROUP_PRECAST_GIRDER = "Precast Girder"
GROUP_CAST_IN_PLACE = "Cast in Place Concrete"
GROUP_STEEL_BEAM = "Steel Beam"
GROUP_STEEL_TRUSS = "Steel Truss"

EXPECTED_RATE_GROUPS = {
    GROUP_STANDARD_OTHER,
    GROUP_PRESTRESSED_CONCRETE,
    GROUP_PRECAST_GIRDER,
    GROUP_CAST_IN_PLACE,
    GROUP_STEEL_BEAM,
    GROUP_STEEL_TRUSS,
}

# Condition bands follow the workbook order. A rating equal to a boundary is
# assigned to the higher band, matching the original project calculation.
CONDITION_BAND_LOWER_BOUNDS = (88.0, 77.0, 66.0, 55.0, 44.0, 33.0, 22.0, 11.0)
EXPECTED_CONDITION_HEADERS = (
    "99 to 88",
    "88 to 77",
    "77 to 66",
    "66 to 55",
    "55 to 44",
    "44 to 33",
    "33 to 22",
    "22 to 11",
)

STANDARD_SPAN_TYPES = {
    "TP",
    "TT",
    "SCC",
    "SM",
    "SMC",
    "VS",
    "VSO",
    "HC",
}

MAJOR_PRESTRESSED_SPAN_TYPES = {
    "CBC",
    "DBC",
    "CBT",
    "DBT",
    "FC",
    "FM",
    "LF",
    "PJ",
    "PM",
    "PO",
    "PQ",
    "RD",
    "RM",
    "VF",
}
MAJOR_PRECAST_SPAN_TYPES = {"PE"}
MAJOR_CAST_IN_PLACE_SPAN_TYPES = {"CA", "CF", "CS", "CT", "CV", "CX"}
MAJOR_STEEL_BEAM_SPAN_TYPES = {"FR", "WG", "RB", "RG"}
MAJOR_STEEL_TRUSS_SPAN_TYPES = {"TH"}

MAJOR_SPAN_TYPES = (
    MAJOR_PRESTRESSED_SPAN_TYPES
    | MAJOR_PRECAST_SPAN_TYPES
    | MAJOR_CAST_IN_PLACE_SPAN_TYPES
    | MAJOR_STEEL_BEAM_SPAN_TYPES
    | MAJOR_STEEL_TRUSS_SPAN_TYPES
)
KNOWN_SPAN_TYPES = STANDARD_SPAN_TYPES | MAJOR_SPAN_TYPES

SPAN_TYPE_TO_CATEGORY = {
    **{code: "STD" for code in STANDARD_SPAN_TYPES},
    **{code: "MAJ" for code in MAJOR_SPAN_TYPES},
}

SPAN_TYPE_TO_GROUP = {
    **{code: GROUP_STANDARD_OTHER for code in STANDARD_SPAN_TYPES},
    **{
        code: GROUP_PRESTRESSED_CONCRETE
        for code in MAJOR_PRESTRESSED_SPAN_TYPES
    },
    **{code: GROUP_PRECAST_GIRDER for code in MAJOR_PRECAST_SPAN_TYPES},
    **{code: GROUP_CAST_IN_PLACE for code in MAJOR_CAST_IN_PLACE_SPAN_TYPES},
    **{code: GROUP_STEEL_BEAM for code in MAJOR_STEEL_BEAM_SPAN_TYPES},
    **{code: GROUP_STEEL_TRUSS for code in MAJOR_STEEL_TRUSS_SPAN_TYPES},
}


class DeteriorationModelError(ValueError):
    """Base error for invalid deterioration inputs or rate tables."""


class DeteriorationRateTableError(DeteriorationModelError):
    """Raised when the workbook deterioration-rate table is invalid."""


class DeteriorationMappingError(DeteriorationModelError):
    """Raised when a bridge record cannot be mapped to the model."""


@dataclass(frozen=True)
class DeteriorationRateTable:
    """Exact annual deterioration rates loaded from the workbook."""

    group_rates: Mapping[str, tuple[float, ...]]
    source_file: str
    source_sheet: str


@dataclass(frozen=True)
class DeteriorationResolution:
    """Auditable mapping from source classification to model groups."""

    original_category: str | None
    original_span_type: str | None
    span_codes: tuple[str, ...]
    resolved_category: str | None
    model_groups: tuple[str, ...]
    method: str
    status: str
    message: str

    @property
    def is_usable(self) -> bool:
        return self.status != "Invalid" and bool(self.model_groups)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def split_span_types(value: Any) -> tuple[str, ...]:
    """Return normalized comma-separated span codes without empty entries."""

    if pd.isna(value):
        return ()

    codes = tuple(
        part.strip().upper()
        for part in str(value).replace("\u00a0", " ").split(",")
        if part.strip()
    )
    return codes


def resolve_deterioration_mapping(
    bridge_category: Any,
    span_type: Any,
) -> DeteriorationResolution:
    """Resolve a source record to one or more deterioration model groups.

    Rules:
    - One known and category-consistent code: direct mapping.
    - One known but category-inconsistent code: infer the model category from
      the span code while preserving the source category as an audit field.
    - Multiple known codes: use all component groups; annual decay later uses
      the maximum component rate as a conservative provisional assumption.
    - Missing or unknown codes: invalid and unusable.
    """

    original_category = _normalize_optional_text(bridge_category)
    original_span_type = _normalize_optional_text(span_type)
    codes = split_span_types(span_type)

    if original_category is None:
        return DeteriorationResolution(
            original_category=None,
            original_span_type=original_span_type,
            span_codes=codes,
            resolved_category=None,
            model_groups=(),
            method="Unresolved",
            status="Invalid",
            message="Bridge category is missing.",
        )

    if original_category not in {"STD", "MAJ"}:
        return DeteriorationResolution(
            original_category=original_category,
            original_span_type=original_span_type,
            span_codes=codes,
            resolved_category=None,
            model_groups=(),
            method="Unresolved",
            status="Invalid",
            message=f"Unsupported bridge category: {original_category}.",
        )

    if not codes:
        return DeteriorationResolution(
            original_category=original_category,
            original_span_type=original_span_type,
            span_codes=(),
            resolved_category=None,
            model_groups=(),
            method="Unresolved",
            status="Invalid",
            message="Span type is missing.",
        )

    unknown_codes = tuple(sorted(set(codes) - KNOWN_SPAN_TYPES))
    if unknown_codes:
        return DeteriorationResolution(
            original_category=original_category,
            original_span_type=original_span_type,
            span_codes=codes,
            resolved_category=None,
            model_groups=(),
            method="Unresolved",
            status="Invalid",
            message="Unknown span-type code(s): " + ", ".join(unknown_codes),
        )

    categories = tuple(SPAN_TYPE_TO_CATEGORY[code] for code in codes)
    model_groups = tuple(dict.fromkeys(SPAN_TYPE_TO_GROUP[code] for code in codes))
    unique_categories = tuple(dict.fromkeys(categories))
    resolved_category = unique_categories[0] if len(unique_categories) == 1 else "MIXED"

    if len(codes) == 1:
        inferred_category = categories[0]
        if inferred_category == original_category:
            return DeteriorationResolution(
                original_category=original_category,
                original_span_type=original_span_type,
                span_codes=codes,
                resolved_category=inferred_category,
                model_groups=model_groups,
                method="Direct span-type mapping",
                status="Direct",
                message="Source category and span type are consistent.",
            )

        return DeteriorationResolution(
            original_category=original_category,
            original_span_type=original_span_type,
            span_codes=codes,
            resolved_category=inferred_category,
            model_groups=model_groups,
            method="Category inferred from span type",
            status="Resolved",
            message=(
                f"Source category '{original_category}' conflicts with span code "
                f"'{codes[0]}'; the deterioration category is resolved as "
                f"'{inferred_category}' without changing the source data."
            ),
        )

    category_note = (
        f"component category '{resolved_category}'"
        if resolved_category != "MIXED"
        else "mixed STD/MAJ component categories"
    )
    return DeteriorationResolution(
        original_category=original_category,
        original_span_type=original_span_type,
        span_codes=codes,
        resolved_category=resolved_category,
        model_groups=model_groups,
        method="Conservative maximum component rate",
        status="Provisional",
        message=(
            "Combined span codes are evaluated separately and the maximum annual "
            f"component deterioration rate is applied ({category_note})."
        ),
    )


def load_deterioration_rates(
    workbook_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
    sheet_name: str = DETERIORATION_RATES_SHEET,
) -> DeteriorationRateTable:
    """Load and validate exact deterioration rates from the source workbook.

    The cache key includes the file modification timestamp, so replacing or
    editing the workbook automatically causes the table to be reloaded.
    """

    path = Path(workbook_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Deterioration workbook not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Deterioration workbook is not a file: {path}")

    stat = path.stat()
    return _load_deterioration_rates_cached(
        str(path),
        stat.st_mtime_ns,
        sheet_name,
    )


def get_deterioration_rate(
    current_rating: float,
    bridge_category: Any,
    span_type: Any,
    rate_table: DeteriorationRateTable,
) -> float:
    """Return the approved annual rate for a bridge at its current rating."""

    if pd.isna(current_rating):
        return float("nan")

    rating = float(current_rating)
    if not np.isfinite(rating):
        raise DeteriorationModelError("Condition rating must be finite.")
    if rating < 0 or rating > 100:
        raise DeteriorationModelError(
            f"Condition rating must be between 0 and 100; received {rating}."
        )

    resolution = resolve_deterioration_mapping(bridge_category, span_type)
    if not resolution.is_usable:
        raise DeteriorationMappingError(resolution.message)

    # The workbook provides no rate below 11. The condition is therefore held
    # at its current low value rather than inventing an unsupported rate.
    if rating < CONDITION_BAND_LOWER_BOUNDS[-1]:
        return 0.0

    band_index = _condition_band_index(rating)
    component_rates = [
        rate_table.group_rates[group][band_index]
        for group in resolution.model_groups
    ]

    if not component_rates:
        raise DeteriorationMappingError(
            "The resolved bridge record has no deterioration model group."
        )

    # Direct and inferred mappings contain one group. Combined spans use the
    # maximum rate as the documented conservative assumption.
    return float(max(component_rates))


def calculate_decay(
    initial_rating: Any,
    bridge_category: Any,
    span_type: Any,
    years: Any,
    rate_table: DeteriorationRateTable,
) -> float:
    """Apply year-by-year deterioration using exact workbook rates."""

    if pd.isna(initial_rating):
        return float("nan")
    if pd.isna(years):
        return float(initial_rating)

    rating = float(initial_rating)
    year_count_float = float(years)

    if not np.isfinite(year_count_float) or year_count_float < 0:
        raise DeteriorationModelError(
            f"Years passed must be a non-negative finite value; received {years}."
        )

    rounded_years = round(year_count_float)
    if not np.isclose(year_count_float, rounded_years):
        raise DeteriorationModelError(
            f"Years passed must be a whole number; received {years}."
        )

    for _ in range(int(rounded_years)):
        annual_rate = get_deterioration_rate(
            current_rating=rating,
            bridge_category=bridge_category,
            span_type=span_type,
            rate_table=rate_table,
        )
        rating = max(0.0, rating - annual_rate)
        if np.isclose(rating, 0.0):
            break

    return round(rating, 2)


def add_deterioration_mapping_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Attach transparent mapping fields without modifying source columns."""

    required = {"Bridge_Cat", "Unique_Span_Type"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(
            "Cannot resolve deterioration mapping; missing column(s): "
            + ", ".join(missing)
        )

    enriched = df.copy()
    resolutions = [
        resolve_deterioration_mapping(row.Bridge_Cat, row.Unique_Span_Type)
        for row in enriched[["Bridge_Cat", "Unique_Span_Type"]].itertuples(index=False)
    ]

    enriched["Resolved_Deterioration_Category"] = pd.Series(
        [item.resolved_category for item in resolutions],
        index=enriched.index,
        dtype="string",
    )
    enriched["Resolved_Deterioration_Group"] = pd.Series(
        [", ".join(item.model_groups) if item.model_groups else pd.NA for item in resolutions],
        index=enriched.index,
        dtype="string",
    )
    enriched["Deterioration_Mapping_Method"] = pd.Series(
        [item.method for item in resolutions],
        index=enriched.index,
        dtype="string",
    )
    enriched["Deterioration_Mapping_Status"] = pd.Series(
        [item.status for item in resolutions],
        index=enriched.index,
        dtype="string",
    )
    enriched["Deterioration_Mapping_Message"] = pd.Series(
        [item.message for item in resolutions],
        index=enriched.index,
        dtype="string",
    )
    return enriched


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
@lru_cache(maxsize=8)
def _load_deterioration_rates_cached(
    path_string: str,
    modified_ns: int,
    sheet_name: str,
) -> DeteriorationRateTable:
    del modified_ns  # Included only to invalidate the cache when the file changes.

    try:
        raw = pd.read_excel(
            path_string,
            sheet_name=sheet_name,
            header=None,
        )
    except ValueError as exc:
        raise DeteriorationRateTableError(
            f"Required sheet '{sheet_name}' was not found in {path_string}."
        ) from exc

    if raw.shape[0] < 9 or raw.shape[1] < 9:
        raise DeteriorationRateTableError(
            "The deterioration-rate sheet does not contain the expected 9 x 9 table."
        )

    headers = tuple(
        str(value).strip() if not pd.isna(value) else ""
        for value in raw.iloc[1, 1:9].tolist()
    )
    if headers != EXPECTED_CONDITION_HEADERS:
        raise DeteriorationRateTableError(
            "Unexpected condition-range headers. Expected "
            f"{EXPECTED_CONDITION_HEADERS}, received {headers}."
        )

    group_rates: dict[str, tuple[float, ...]] = {}
    for row_index in range(3, len(raw)):
        group_value = raw.iat[row_index, 0]
        if pd.isna(group_value):
            continue

        group_name = str(group_value).strip()
        if group_name not in EXPECTED_RATE_GROUPS:
            continue

        numeric_rates = pd.to_numeric(
            raw.iloc[row_index, 1:9],
            errors="coerce",
        )
        if numeric_rates.isna().any():
            raise DeteriorationRateTableError(
                f"Rate row '{group_name}' contains missing or non-numeric values."
            )

        rates = tuple(float(value) for value in numeric_rates.tolist())
        if any((not np.isfinite(value)) or value < 0 for value in rates):
            raise DeteriorationRateTableError(
                f"Rate row '{group_name}' contains an invalid negative or non-finite value."
            )
        group_rates[group_name] = rates

    missing_groups = sorted(EXPECTED_RATE_GROUPS - set(group_rates))
    if missing_groups:
        raise DeteriorationRateTableError(
            "The deterioration-rate sheet is missing model group(s): "
            + ", ".join(missing_groups)
        )

    return DeteriorationRateTable(
        group_rates=group_rates,
        source_file=path_string,
        source_sheet=sheet_name,
    )


def _condition_band_index(rating: float) -> int:
    for index, lower_bound in enumerate(CONDITION_BAND_LOWER_BOUNDS):
        if rating >= lower_bound:
            return index
    raise DeteriorationModelError(
        f"No workbook deterioration band is defined for rating {rating}."
    )


def _normalize_optional_text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    normalized = str(value).replace("\u00a0", " ").strip().upper()
    return normalized or None
