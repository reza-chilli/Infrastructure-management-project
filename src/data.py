"""Bridge dataset loading, cleaning, and validation utilities.

The module keeps the application's analysis year dynamic by default. Every call
uses the current calendar year unless a different year is explicitly supplied
for testing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable
import re

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Workbook schema
# ---------------------------------------------------------------------------
DEFAULT_EXCEL_FILE_PATH = "ToR Structures_Data_Updated- bahman 1405.xlsx"
BRIDGE_DATA_SHEET = "Bridge Data"
DETERIORATION_RATES_SHEET = "Bridge Deterioration Rates"
HEADER_ROW_COUNT = 2
EXCEL_DATA_START_ROW = HEADER_ROW_COUNT + 1

COLUMN_NAMES = [
    "Structure_ID",
    "Bridge_Cat",
    "Hwy_ID",
    "Hwy_Dir",
    "KM",
    "Usage_Code",
    "Replacement_Cost",
    "First_Year_In_Service",
    "Unique_Span_Type",
    "Max_Span_Ln",
    "No_of_Spans",
    "Nominal_Bridge_Ln",
    "Total_Clear_Roadway",
    "Cond_Rat_Deck",
    "Cond_Rat_Super",
    "Cond_Rat_Sub",
    "Insp_Date",
    "Traffic_Volume",
]

TEXT_COLUMNS = [
    "Structure_ID",
    "Bridge_Cat",
    "Hwy_ID",
    "Hwy_Dir",
    "Usage_Code",
    "Unique_Span_Type",
]

UPPERCASE_TEXT_COLUMNS = [
    "Structure_ID",
    "Bridge_Cat",
    "Hwy_ID",
    "Hwy_Dir",
    "Usage_Code",
    "Unique_Span_Type",
]

NUMERIC_COLUMNS = [
    "KM",
    "Replacement_Cost",
    "First_Year_In_Service",
    "Max_Span_Ln",
    "No_of_Spans",
    "Nominal_Bridge_Ln",
    "Total_Clear_Roadway",
    "Cond_Rat_Deck",
    "Cond_Rat_Super",
    "Cond_Rat_Sub",
    "Traffic_Volume",
]

INTEGER_COLUMNS = [
    "First_Year_In_Service",
    "No_of_Spans",
    "Traffic_Volume",
]

CONDITION_COLUMNS = [
    "Cond_Rat_Deck",
    "Cond_Rat_Super",
    "Cond_Rat_Sub",
]

# These fields are needed for the full lifecycle, treatment-cost, and priority
# analyses. Usage_Code is intentionally optional because it is missing in many
# source records and is not used by the current calculations.
REQUIRED_VALUE_COLUMNS = [
    "Structure_ID",
    "Bridge_Cat",
    "Hwy_ID",
    "Hwy_Dir",
    "KM",
    "Replacement_Cost",
    "First_Year_In_Service",
    "Unique_Span_Type",
    "Max_Span_Ln",
    "No_of_Spans",
    "Nominal_Bridge_Ln",
    "Total_Clear_Roadway",
    "Cond_Rat_Deck",
    "Cond_Rat_Super",
    "Cond_Rat_Sub",
    "Inspection_Year",
    "Traffic_Volume",
]

OPTIONAL_VALUE_COLUMNS = ["Usage_Code"]

ALLOWED_BRIDGE_CATEGORIES = {"STD", "MAJ"}
ALLOWED_HIGHWAY_DIRECTIONS = {"C", "L", "R"}

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

MAJOR_SPAN_TYPES = {
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
    "PE",
    "CA",
    "CF",
    "CS",
    "CT",
    "CV",
    "CX",
    "FR",
    "WG",
    "RB",
    "RG",
    "TH",
}

KNOWN_SPAN_TYPES = STANDARD_SPAN_TYPES | MAJOR_SPAN_TYPES

# Numeric fields where unusual values should be reviewed, not automatically
# removed or capped. Infrastructure assets can legitimately be outliers.
OUTLIER_COLUMNS = [
    "Replacement_Cost",
    "Max_Span_Ln",
    "No_of_Spans",
    "Nominal_Bridge_Ln",
    "Total_Clear_Roadway",
    "Cond_Rat_Deck",
    "Cond_Rat_Super",
    "Cond_Rat_Sub",
    "Traffic_Volume",
]

_HEADER_EXPECTATIONS = {
    (0, 0): "Structure ID",
    (0, 1): "Bridge Cat",
    (0, 2): "Hwy ID",
    (0, 3): "Hwy Dir",
    (0, 4): "KM",
    (0, 5): "Usage Code",
    (0, 6): "Replacement Cost ($2020)",
    (0, 7): "First Year In Service",
    (0, 8): "Unique Span Type",
    (0, 9): "Max Span Ln (m)",
    (0, 10): "No of Spans",
    (0, 11): "Nominal Bridge Ln (m)",
    (0, 12): "Total Clear Roadway (m)",
    (0, 13): "Cond Rat",
    (1, 13): "Deck",
    (1, 14): "Super",
    (1, 15): "Sub",
    (0, 16): "Insp Date",
    (0, 17): "Traffic Volume (AADT)",
}


# ---------------------------------------------------------------------------
# Result objects and exceptions
# ---------------------------------------------------------------------------
class DataSchemaError(ValueError):
    """Raised when the workbook structure is incompatible with the project."""


@dataclass(frozen=True)
class DataValidationResult:
    """Cleaned bridge data together with a complete validation report."""

    data: pd.DataFrame
    issues: pd.DataFrame
    column_profile: pd.DataFrame
    summary: dict[str, Any]
    source_file: str
    source_sheet: str
    analysis_year: int

    @property
    def has_critical_issues(self) -> bool:
        return bool(self.summary.get("critical_issue_count", 0))

    @property
    def is_core_analysis_ready(self) -> bool:
        return not self.has_critical_issues

    @property
    def is_deterioration_model_ready(self) -> bool:
        return bool(self.summary.get("deterioration_model_ready", False))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_current_year() -> int:
    """Return the current calendar year used by the live analysis."""

    return date.today().year


def load_bridge_data(
    file_path: str | Path,
    sheet_name: str = BRIDGE_DATA_SHEET,
) -> pd.DataFrame:
    """Load raw bridge rows after validating the workbook schema.

    This function performs structural validation only. Use
    :func:`load_and_validate_data` for the complete cleaning and validation
    pipeline.
    """

    path = _validate_file_path(file_path)
    _validate_workbook_schema(path, sheet_name)

    raw = pd.read_excel(
        path,
        sheet_name=sheet_name,
        skiprows=HEADER_ROW_COUNT,
        header=None,
        usecols=range(len(COLUMN_NAMES)),
        engine="openpyxl",
    )

    raw = raw.dropna(how="all").reset_index(drop=True)

    if raw.shape[1] != len(COLUMN_NAMES):
        raise DataSchemaError(
            f"Expected {len(COLUMN_NAMES)} data columns in sheet "
            f"'{sheet_name}', but found {raw.shape[1]}."
        )

    raw.columns = COLUMN_NAMES
    return raw


def preprocess_bridge_data(
    df: pd.DataFrame,
    current_year: int | None = None,
) -> pd.DataFrame:
    """Clean text, coerce numeric fields, and derive inspection variables.

    The function remains compatible with the existing application: it returns
    only the cleaned DataFrame and keeps both ``Inspection_Year`` and the legacy
    alias ``Insp_Year``.
    """

    analysis_year = current_year if current_year is not None else get_current_year()
    cleaned, _ = _clean_bridge_dataframe(df, analysis_year)
    return cleaned


def validate_bridge_data(
    df: pd.DataFrame,
    current_year: int | None = None,
    conversion_failures: pd.DataFrame | None = None,
) -> DataValidationResult:
    """Validate an already cleaned bridge DataFrame.

    Prefer :func:`load_and_validate_data` when loading from Excel because it can
    also report numeric-conversion failures from the original cell values.
    """

    analysis_year = current_year if current_year is not None else get_current_year()
    cleaned = df.copy()

    if "Inspection_Year" not in cleaned.columns or "Years_Passed" not in cleaned.columns:
        cleaned, detected_failures = _clean_bridge_dataframe(cleaned, analysis_year)
        if conversion_failures is None:
            conversion_failures = detected_failures

    issues = _build_validation_issues(
        cleaned,
        analysis_year,
        conversion_failures=conversion_failures,
    )
    enriched = _attach_row_quality_fields(cleaned, issues)
    profile = _build_column_profile(enriched)
    summary = _build_validation_summary(enriched, issues, analysis_year)

    return DataValidationResult(
        data=enriched,
        issues=issues,
        column_profile=profile,
        summary=summary,
        source_file="In-memory DataFrame",
        source_sheet=BRIDGE_DATA_SHEET,
        analysis_year=analysis_year,
    )


def load_and_validate_data(
    file_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
    sheet_name: str = BRIDGE_DATA_SHEET,
    current_year: int | None = None,
) -> DataValidationResult:
    """Load, clean, validate, and profile the bridge dataset."""

    analysis_year = current_year if current_year is not None else get_current_year()
    path = _validate_file_path(file_path)
    raw = load_bridge_data(path, sheet_name=sheet_name)
    cleaned, conversion_failures = _clean_bridge_dataframe(raw, analysis_year)
    issues = _build_validation_issues(
        cleaned,
        analysis_year,
        conversion_failures=conversion_failures,
    )
    enriched = _attach_row_quality_fields(cleaned, issues)
    profile = _build_column_profile(enriched)
    summary = _build_validation_summary(enriched, issues, analysis_year)

    return DataValidationResult(
        data=enriched,
        issues=issues,
        column_profile=profile,
        summary=summary,
        source_file=str(path.resolve()),
        source_sheet=sheet_name,
        analysis_year=analysis_year,
    )


def load_and_preprocess_data(
    file_path: str | Path = DEFAULT_EXCEL_FILE_PATH,
    current_year: int | None = None,
    return_validation: bool = False,
) -> pd.DataFrame | DataValidationResult:
    """Backward-compatible entry point used by ``app.py``.

    Existing code can continue receiving a DataFrame. Set
    ``return_validation=True`` to receive the full :class:`DataValidationResult`.
    """

    result = load_and_validate_data(
        file_path=file_path,
        current_year=current_year,
    )
    return result if return_validation else result.data


# ---------------------------------------------------------------------------
# Workbook and schema validation
# ---------------------------------------------------------------------------
def _validate_file_path(file_path: str | Path) -> Path:
    path = Path(file_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Bridge data workbook was not found: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Bridge data path is not a file: {path}")
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise DataSchemaError(
            f"Expected an Excel workbook (.xlsx or .xlsm), received: {path.suffix}"
        )
    return path


def _validate_workbook_schema(path: Path, sheet_name: str) -> None:
    try:
        workbook = pd.ExcelFile(path, engine="openpyxl")
    except Exception as exc:  # pragma: no cover - library-specific error details
        raise DataSchemaError(f"The Excel workbook could not be opened: {exc}") from exc

    if sheet_name not in workbook.sheet_names:
        raise DataSchemaError(
            f"Required sheet '{sheet_name}' was not found. Available sheets: "
            + ", ".join(workbook.sheet_names)
        )

    header = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=None,
        nrows=HEADER_ROW_COUNT,
        engine="openpyxl",
    )

    if header.shape[1] != len(COLUMN_NAMES):
        raise DataSchemaError(
            f"Sheet '{sheet_name}' must contain exactly {len(COLUMN_NAMES)} "
            f"columns, but {header.shape[1]} were detected."
        )

    mismatches: list[str] = []
    for (row_index, column_index), expected in _HEADER_EXPECTATIONS.items():
        actual = _normalize_header_value(header.iat[row_index, column_index])
        if actual != _normalize_header_value(expected):
            mismatches.append(
                f"cell ({row_index + 1}, {column_index + 1}): "
                f"expected '{expected}', found '{actual or '<blank>'}'"
            )

    if mismatches:
        raise DataSchemaError(
            "The 'Bridge Data' header structure has changed:\n- "
            + "\n- ".join(mismatches)
        )


def _normalize_header_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).replace("\u00a0", " ")).strip()


# ---------------------------------------------------------------------------
# Cleaning and coercion
# ---------------------------------------------------------------------------
def _clean_bridge_dataframe(
    df: pd.DataFrame,
    analysis_year: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = [column for column in COLUMN_NAMES if column not in df.columns]
    if missing_columns:
        raise DataSchemaError(
            "The bridge DataFrame is missing required source columns: "
            + ", ".join(missing_columns)
        )

    cleaned = df[COLUMN_NAMES].copy()
    cleaned = cleaned.dropna(how="all").reset_index(drop=True)

    # Preserve the original source-row position for clear validation messages.
    cleaned["Source_Row"] = cleaned.index + EXCEL_DATA_START_ROW

    for column in TEXT_COLUMNS:
        cleaned[column] = _clean_text_series(cleaned[column])

    for column in UPPERCASE_TEXT_COLUMNS:
        cleaned[column] = cleaned[column].str.upper()

    cleaned["Unique_Span_Type"] = cleaned["Unique_Span_Type"].map(
        _normalize_span_type_value,
        na_action="ignore",
    ).astype("string")

    conversion_failure_rows: list[dict[str, Any]] = []

    for column in NUMERIC_COLUMNS:
        original = cleaned[column].copy()
        converted = _coerce_numeric_series(original)
        failed = original.notna() & converted.isna()

        for index in cleaned.index[failed]:
            conversion_failure_rows.append(
                {
                    "Data_Index": int(index),
                    "Source_Row": int(cleaned.at[index, "Source_Row"]),
                    "Structure_ID": cleaned.at[index, "Structure_ID"],
                    "Column": column,
                    "Original_Value": original.at[index],
                }
            )

        cleaned[column] = converted.astype("Float64")

    inspection_year, inspection_failures = _extract_inspection_year(
        cleaned["Insp_Date"],
        cleaned,
    )
    conversion_failure_rows.extend(inspection_failures)

    cleaned["Inspection_Year"] = inspection_year.astype("Int64")
    # Keep the legacy alias because calculations.py currently expects Insp_Year.
    cleaned["Insp_Year"] = cleaned["Inspection_Year"]
    cleaned["Years_Passed"] = (
        analysis_year - cleaned["Inspection_Year"]
    ).astype("Int64")

    for column in INTEGER_COLUMNS:
        numeric = cleaned[column]
        integer_mask = numeric.isna() | np.isclose(numeric % 1, 0)
        if integer_mask.all():
            cleaned[column] = numeric.round().astype("Int64")

    failures = pd.DataFrame(
        conversion_failure_rows,
        columns=[
            "Data_Index",
            "Source_Row",
            "Structure_ID",
            "Column",
            "Original_Value",
        ],
    )

    return cleaned, failures


def _clean_text_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string")
    cleaned = cleaned.str.replace("\u00a0", " ", regex=False)
    cleaned = cleaned.str.replace("\u202f", " ", regex=False)
    cleaned = cleaned.str.replace("\u200b", "", regex=False)
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True).str.strip()
    return cleaned.mask(cleaned.eq(""), pd.NA)


def _normalize_span_type_value(value: Any) -> Any:
    if pd.isna(value):
        return pd.NA
    parts = [part.strip().upper() for part in str(value).split(",")]
    parts = [part for part in parts if part]
    return ",".join(parts) if parts else pd.NA


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    text = series.astype("string")
    text = text.str.replace("\u00a0", " ", regex=False).str.strip()
    text = text.str.replace(",", "", regex=False)
    text = text.str.replace(r"[$€£]", "", regex=True)
    text = text.replace(
        {
            "": pd.NA,
            "-": pd.NA,
            "--": pd.NA,
            "N/A": pd.NA,
            "NA": pd.NA,
            "NONE": pd.NA,
            "NULL": pd.NA,
            "UNKNOWN": pd.NA,
        }
    )
    return pd.to_numeric(text, errors="coerce")


def _extract_inspection_year(
    series: pd.Series,
    frame: pd.DataFrame,
) -> tuple[pd.Series, list[dict[str, Any]]]:
    years = pd.Series(pd.NA, index=series.index, dtype="Int64")
    failures: list[dict[str, Any]] = []

    for index, value in series.items():
        if pd.isna(value):
            continue

        parsed_year = _parse_year_value(value)
        if parsed_year is None:
            failures.append(
                {
                    "Data_Index": int(index),
                    "Source_Row": int(frame.at[index, "Source_Row"]),
                    "Structure_ID": frame.at[index, "Structure_ID"],
                    "Column": "Insp_Date",
                    "Original_Value": value,
                }
            )
        else:
            years.at[index] = parsed_year

    return years, failures


def _parse_year_value(value: Any) -> int | None:
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return int(value.year)

    if isinstance(value, (int, np.integer)):
        integer_value = int(value)
        if 1800 <= integer_value <= 2200:
            return integer_value
        if 20_000 <= integer_value <= 100_000:
            try:
                return int(
                    pd.to_datetime(
                        integer_value,
                        unit="D",
                        origin="1899-12-30",
                    ).year
                )
            except (ValueError, OverflowError):
                return None

    if isinstance(value, (float, np.floating)) and np.isfinite(value):
        if float(value).is_integer():
            return _parse_year_value(int(value))

    text = str(value).strip()
    four_digit_years = re.findall(r"(?<!\d)(18\d{2}|19\d{2}|20\d{2}|21\d{2})(?!\d)", text)
    if four_digit_years:
        return int(four_digit_years[-1])

    try:
        parsed = pd.to_datetime(text, errors="raise")
        return int(parsed.year)
    except (ValueError, TypeError, OverflowError):
        return None


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------
def _build_validation_issues(
    df: pd.DataFrame,
    analysis_year: int,
    conversion_failures: pd.DataFrame | None,
) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []

    def add_issue(
        index: int | None,
        severity: str,
        category: str,
        column: str | None,
        value: Any,
        message: str,
        suggested_action: str,
    ) -> None:
        structure_id: Any = pd.NA
        source_row: Any = pd.NA
        if index is not None and index in df.index:
            structure_id = df.at[index, "Structure_ID"]
            source_row = df.at[index, "Source_Row"]

        issues.append(
            {
                "Data_Index": index if index is not None else pd.NA,
                "Source_Row": source_row,
                "Structure_ID": structure_id,
                "Severity": severity,
                "Category": category,
                "Column": column,
                "Value": value,
                "Message": message,
                "Suggested_Action": suggested_action,
            }
        )

    # Conversion failures are critical because the affected source cell cannot
    # participate reliably in numeric analysis.
    if conversion_failures is not None and not conversion_failures.empty:
        for failure in conversion_failures.to_dict("records"):
            add_issue(
                int(failure["Data_Index"]),
                "Critical",
                "Type Conversion",
                str(failure["Column"]),
                failure["Original_Value"],
                "A non-empty source value could not be converted to the required numeric or year type.",
                "Correct the source cell or use a supported numeric/date representation.",
            )

    # Missing required values.
    for column in REQUIRED_VALUE_COLUMNS:
        for index in df.index[df[column].isna()]:
            add_issue(
                int(index),
                "Critical",
                "Missing Required Value",
                column,
                pd.NA,
                f"Required field '{column}' is missing.",
                "Complete the source value before using this record in analysis.",
            )

    for column in OPTIONAL_VALUE_COLUMNS:
        for index in df.index[df[column].isna()]:
            add_issue(
                int(index),
                "Warning",
                "Missing Optional Value",
                column,
                pd.NA,
                f"Optional field '{column}' is missing.",
                "Confirm whether the value is unavailable; do not impute it without a defensible rule.",
            )

    # Duplicate keys.
    duplicate_mask = df["Structure_ID"].notna() & df["Structure_ID"].duplicated(keep=False)
    for index in df.index[duplicate_mask]:
        add_issue(
            int(index),
            "Critical",
            "Duplicate Identifier",
            "Structure_ID",
            df.at[index, "Structure_ID"],
            "Structure_ID is duplicated; bridge records must be uniquely identifiable.",
            "Resolve the duplicate in the source workbook before aggregating or ranking assets.",
        )

    # Allowed categorical values.
    invalid_category = df["Bridge_Cat"].notna() & ~df["Bridge_Cat"].isin(ALLOWED_BRIDGE_CATEGORIES)
    for index in df.index[invalid_category]:
        add_issue(
            int(index),
            "Critical",
            "Invalid Category",
            "Bridge_Cat",
            df.at[index, "Bridge_Cat"],
            "Bridge category is not one of the supported values: STD or MAJ.",
            "Correct or formally map the bridge category.",
        )

    invalid_direction = df["Hwy_Dir"].notna() & ~df["Hwy_Dir"].isin(ALLOWED_HIGHWAY_DIRECTIONS)
    for index in df.index[invalid_direction]:
        add_issue(
            int(index),
            "Warning",
            "Invalid Category",
            "Hwy_Dir",
            df.at[index, "Hwy_Dir"],
            "Highway direction is outside the expected C/L/R codes.",
            "Confirm the direction code and add an approved mapping if necessary.",
        )

    # Numeric ranges and logical relationships.
    for column in CONDITION_COLUMNS:
        invalid = df[column].notna() & ~df[column].between(0, 100, inclusive="both")
        for index in df.index[invalid]:
            add_issue(
                int(index),
                "Critical",
                "Out of Range",
                column,
                df.at[index, column],
                "Condition rating must be between 0 and 100.",
                "Verify the inspection rating in the source workbook.",
            )

    _add_nonpositive_issues(
        df,
        issues,
        columns=[
            "Replacement_Cost",
            "Max_Span_Ln",
            "Nominal_Bridge_Ln",
            "Total_Clear_Roadway",
        ],
        severity="Critical",
        allow_zero=False,
    )

    invalid_spans = df["No_of_Spans"].notna() & (
        (df["No_of_Spans"] <= 0)
        | ~np.isclose(df["No_of_Spans"].astype(float) % 1, 0)
    )
    for index in df.index[invalid_spans]:
        add_issue(
            int(index),
            "Critical",
            "Invalid Numeric Value",
            "No_of_Spans",
            df.at[index, "No_of_Spans"],
            "Number of spans must be a positive whole number.",
            "Correct the source value.",
        )

    negative_traffic = df["Traffic_Volume"].notna() & (df["Traffic_Volume"] < 0)
    for index in df.index[negative_traffic]:
        add_issue(
            int(index),
            "Critical",
            "Out of Range",
            "Traffic_Volume",
            df.at[index, "Traffic_Volume"],
            "Traffic volume cannot be negative.",
            "Correct the AADT value in the source workbook.",
        )

    zero_traffic = df["Traffic_Volume"].notna() & (df["Traffic_Volume"] == 0)
    for index in df.index[zero_traffic]:
        add_issue(
            int(index),
            "Warning",
            "Review Numeric Value",
            "Traffic_Volume",
            df.at[index, "Traffic_Volume"],
            "Traffic volume is zero and should be confirmed.",
            "Confirm whether the asset is closed, unused, or missing an AADT estimate.",
        )

    negative_km = df["KM"].notna() & (df["KM"] < 0)
    for index in df.index[negative_km]:
        add_issue(
            int(index),
            "Critical",
            "Out of Range",
            "KM",
            df.at[index, "KM"],
            "Route kilometre cannot be negative.",
            "Correct the route-location value.",
        )

    zero_km = df["KM"].notna() & (df["KM"] == 0)
    for index in df.index[zero_km]:
        add_issue(
            int(index),
            "Warning",
            "Review Numeric Value",
            "KM",
            df.at[index, "KM"],
            "Route kilometre is zero; this may be valid but should be confirmed.",
            "Verify that the bridge is located at the route origin.",
        )

    invalid_service_year = df["First_Year_In_Service"].notna() & (
        (df["First_Year_In_Service"] < 1800)
        | (df["First_Year_In_Service"] > analysis_year)
        | ~np.isclose(df["First_Year_In_Service"].astype(float) % 1, 0)
    )
    for index in df.index[invalid_service_year]:
        add_issue(
            int(index),
            "Critical",
            "Invalid Year",
            "First_Year_In_Service",
            df.at[index, "First_Year_In_Service"],
            f"First year in service must be a whole year between 1800 and {analysis_year}.",
            "Correct the commissioning year.",
        )

    invalid_inspection_year = df["Inspection_Year"].notna() & (
        (df["Inspection_Year"] < 1800)
        | (df["Inspection_Year"] > analysis_year)
    )
    for index in df.index[invalid_inspection_year]:
        add_issue(
            int(index),
            "Critical",
            "Invalid Year",
            "Inspection_Year",
            df.at[index, "Inspection_Year"],
            f"Inspection year must be between 1800 and the current analysis year ({analysis_year}).",
            "Correct the inspection date/year.",
        )

    inspection_before_service = (
        df["Inspection_Year"].notna()
        & df["First_Year_In_Service"].notna()
        & (df["Inspection_Year"] < df["First_Year_In_Service"])
    )
    for index in df.index[inspection_before_service]:
        add_issue(
            int(index),
            "Critical",
            "Logical Inconsistency",
            "Inspection_Year",
            df.at[index, "Inspection_Year"],
            "Inspection year is earlier than the first year in service.",
            "Verify both dates in the source workbook.",
        )

    negative_years_passed = df["Years_Passed"].notna() & (df["Years_Passed"] < 0)
    for index in df.index[negative_years_passed]:
        add_issue(
            int(index),
            "Critical",
            "Logical Inconsistency",
            "Years_Passed",
            df.at[index, "Years_Passed"],
            "Years passed since inspection cannot be negative.",
            "Correct the inspection year.",
        )

    # Span-type and deterioration mapping review. These are warnings for now so
    # the user can inspect the existing dashboard, but the summary separately
    # indicates that the deterioration model is not ready.
    for index, row in df.iterrows():
        span_value = row["Unique_Span_Type"]
        category = row["Bridge_Cat"]
        if pd.isna(span_value) or pd.isna(category):
            continue

        codes = _split_span_types(span_value)
        unknown_codes = sorted(set(codes) - KNOWN_SPAN_TYPES)

        if unknown_codes:
            add_issue(
                int(index),
                "Warning",
                "Unknown Span Type",
                "Unique_Span_Type",
                span_value,
                "One or more span-type codes are not defined in the current project taxonomy: "
                + ", ".join(unknown_codes),
                "Confirm the code definitions and add an approved deterioration mapping.",
            )

        if len(codes) > 1:
            add_issue(
                int(index),
                "Warning",
                "Combined Span Type",
                "Unique_Span_Type",
                span_value,
                "The record contains multiple span-type codes, while the current deterioration lookup expects one code.",
                "Define a documented rule for combined spans before final deterioration analysis.",
            )

        expected_set = STANDARD_SPAN_TYPES if category == "STD" else MAJOR_SPAN_TYPES
        mismatched_codes = sorted(set(codes) - expected_set)
        if mismatched_codes:
            add_issue(
                int(index),
                "Warning",
                "Category/Span Mismatch",
                "Unique_Span_Type",
                span_value,
                f"Span type is inconsistent with bridge category '{category}': "
                + ", ".join(mismatched_codes),
                "Verify Bridge_Cat and Unique_Span_Type against the source classification.",
            )

    # IQR outlier detection. Outliers are informational and are never changed.
    for column in OUTLIER_COLUMNS:
        numeric = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(numeric) < 4:
            continue
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or np.isclose(iqr, 0):
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = df[column].notna() & ((df[column] < lower) | (df[column] > upper))
        for index in df.index[mask]:
            add_issue(
                int(index),
                "Info",
                "Statistical Outlier",
                column,
                df.at[index, column],
                f"Value falls outside the IQR review range [{lower:.3g}, {upper:.3g}].",
                "Review against source records; do not remove or cap automatically.",
            )

    issue_columns = [
        "Data_Index",
        "Source_Row",
        "Structure_ID",
        "Severity",
        "Category",
        "Column",
        "Value",
        "Message",
        "Suggested_Action",
    ]
    issue_frame = pd.DataFrame(issues, columns=issue_columns)

    if issue_frame.empty:
        return issue_frame

    severity_order = pd.CategoricalDtype(
        categories=["Critical", "Warning", "Info"],
        ordered=True,
    )
    issue_frame["Severity"] = issue_frame["Severity"].astype(severity_order)
    issue_frame = issue_frame.sort_values(
        ["Severity", "Source_Row", "Category", "Column"],
        na_position="last",
    ).reset_index(drop=True)
    issue_frame["Severity"] = issue_frame["Severity"].astype("string")
    return issue_frame


def _add_nonpositive_issues(
    df: pd.DataFrame,
    issues: list[dict[str, Any]],
    columns: Iterable[str],
    severity: str,
    allow_zero: bool,
) -> None:
    comparator = (lambda values: values < 0) if allow_zero else (lambda values: values <= 0)

    for column in columns:
        mask = df[column].notna() & comparator(df[column])
        for index in df.index[mask]:
            issues.append(
                {
                    "Data_Index": int(index),
                    "Source_Row": df.at[index, "Source_Row"],
                    "Structure_ID": df.at[index, "Structure_ID"],
                    "Severity": severity,
                    "Category": "Out of Range",
                    "Column": column,
                    "Value": df.at[index, column],
                    "Message": f"'{column}' must be greater than zero.",
                    "Suggested_Action": "Verify and correct the source value.",
                }
            )


def _split_span_types(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip().upper() for part in str(value).split(",") if part.strip()]


# ---------------------------------------------------------------------------
# Reporting fields
# ---------------------------------------------------------------------------
def _attach_row_quality_fields(
    df: pd.DataFrame,
    issues: pd.DataFrame,
) -> pd.DataFrame:
    enriched = df.copy()

    for column, default in [
        ("Data_Quality_Issue_Count", 0),
        ("Data_Quality_Critical_Count", 0),
        ("Data_Quality_Warning_Count", 0),
        ("Data_Quality_Info_Count", 0),
    ]:
        enriched[column] = default

    enriched["Data_Quality_Status"] = "Valid"
    enriched["Outlier_Columns"] = pd.Series(pd.NA, index=enriched.index, dtype="string")
    enriched["Deterioration_Mapping_Status"] = "Valid"

    if issues.empty:
        return enriched

    row_issues = issues.dropna(subset=["Data_Index"]).copy()
    row_issues["Data_Index"] = row_issues["Data_Index"].astype(int)

    total_counts = row_issues.groupby("Data_Index").size()
    critical_counts = row_issues[row_issues["Severity"] == "Critical"].groupby("Data_Index").size()
    warning_counts = row_issues[row_issues["Severity"] == "Warning"].groupby("Data_Index").size()
    info_counts = row_issues[row_issues["Severity"] == "Info"].groupby("Data_Index").size()

    enriched.loc[total_counts.index, "Data_Quality_Issue_Count"] = total_counts
    enriched.loc[critical_counts.index, "Data_Quality_Critical_Count"] = critical_counts
    enriched.loc[warning_counts.index, "Data_Quality_Warning_Count"] = warning_counts
    enriched.loc[info_counts.index, "Data_Quality_Info_Count"] = info_counts

    enriched.loc[warning_counts.index, "Data_Quality_Status"] = "Review"
    enriched.loc[critical_counts.index, "Data_Quality_Status"] = "Invalid"

    outlier_issues = row_issues[row_issues["Category"] == "Statistical Outlier"]
    if not outlier_issues.empty:
        outlier_columns = outlier_issues.groupby("Data_Index")["Column"].agg(
            lambda values: ", ".join(sorted(set(values.dropna().astype(str))))
        )
        enriched.loc[outlier_columns.index, "Outlier_Columns"] = outlier_columns.astype("string")

    mapping_categories = {
        "Unknown Span Type",
        "Combined Span Type",
        "Category/Span Mismatch",
    }
    mapping_issues = row_issues[row_issues["Category"].isin(mapping_categories)]
    if not mapping_issues.empty:
        enriched.loc[mapping_issues["Data_Index"].unique(), "Deterioration_Mapping_Status"] = "Review"

    # The current deterioration function can map only one valid code. Mark all
    # records that violate that requirement as Unmapped.
    for index, row in enriched.iterrows():
        codes = _split_span_types(row["Unique_Span_Type"])
        category = row["Bridge_Cat"]
        if not codes or category not in ALLOWED_BRIDGE_CATEGORIES:
            enriched.at[index, "Deterioration_Mapping_Status"] = "Unmapped"
            continue
        expected_set = STANDARD_SPAN_TYPES if category == "STD" else MAJOR_SPAN_TYPES
        if len(codes) != 1 or codes[0] not in expected_set:
            enriched.at[index, "Deterioration_Mapping_Status"] = "Unmapped"

    return enriched


def _build_column_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    row_count = len(df)

    for column in df.columns:
        series = df[column]
        non_null = int(series.notna().sum())
        missing = row_count - non_null
        profile: dict[str, Any] = {
            "Column": column,
            "Dtype": str(series.dtype),
            "Rows": row_count,
            "Non_Null": non_null,
            "Missing": missing,
            "Missing_Percent": round((missing / row_count * 100), 2) if row_count else 0.0,
            "Unique": int(series.nunique(dropna=True)),
            "Minimum": pd.NA,
            "Maximum": pd.NA,
        }

        if pd.api.types.is_numeric_dtype(series):
            valid = pd.to_numeric(series, errors="coerce").dropna()
            if not valid.empty:
                profile["Minimum"] = float(valid.min())
                profile["Maximum"] = float(valid.max())

        rows.append(profile)

    return pd.DataFrame(rows)


def _build_validation_summary(
    df: pd.DataFrame,
    issues: pd.DataFrame,
    analysis_year: int,
) -> dict[str, Any]:
    severity_counts = (
        issues["Severity"].value_counts().to_dict() if not issues.empty else {}
    )
    status_counts = df["Data_Quality_Status"].value_counts().to_dict()
    mapping_counts = df["Deterioration_Mapping_Status"].value_counts().to_dict()

    critical_count = int(severity_counts.get("Critical", 0))
    unmapped_count = int(mapping_counts.get("Unmapped", 0))

    return {
        "analysis_year": analysis_year,
        "row_count": int(len(df)),
        "source_column_count": len(COLUMN_NAMES),
        "total_missing_cells": int(df[COLUMN_NAMES].isna().sum().sum()),
        "duplicate_structure_id_count": int(
            (
                df["Structure_ID"].notna()
                & df["Structure_ID"].duplicated(keep=False)
            ).sum()
        ),
        "critical_issue_count": critical_count,
        "warning_issue_count": int(severity_counts.get("Warning", 0)),
        "info_issue_count": int(severity_counts.get("Info", 0)),
        "valid_row_count": int(status_counts.get("Valid", 0)),
        "review_row_count": int(status_counts.get("Review", 0)),
        "invalid_row_count": int(status_counts.get("Invalid", 0)),
        "unmapped_deterioration_record_count": unmapped_count,
        "core_analysis_ready": critical_count == 0,
        "deterioration_model_ready": unmapped_count == 0,
    }
