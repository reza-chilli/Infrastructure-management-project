"""Streamlit view for bridge-data cleaning and validation results."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data import DataValidationResult


def render_data_quality_page(result: DataValidationResult) -> None:
    """Render dataset readiness, issues, profiles, and downloadable reports."""

    st.title("Data Quality & Validation")
    st.caption(
        f"Source: {result.source_file} | Sheet: {result.source_sheet} | "
        f"Live analysis year: {result.analysis_year}"
    )

    summary = result.summary

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Bridge Records", f"{summary['row_count']:,}")
    col2.metric("Critical Issues", f"{summary['critical_issue_count']:,}")
    col3.metric("Warnings", f"{summary['warning_issue_count']:,}")
    col4.metric("Missing Source Cells", f"{summary['total_missing_cells']:,}")
    col5.metric(
        "Unmapped Deterioration",
        f"{summary['unmapped_deterioration_record_count']:,}",
    )

    if result.is_core_analysis_ready:
        st.success(
            "The dataset passed the structural, type, required-value, range, "
            "duplicate, and cross-field checks required for core analysis."
        )
    else:
        st.error(
            "Critical data issues were detected. Core calculations should be "
            "stopped until the listed records are corrected."
        )

    if result.is_deterioration_model_ready:
        st.success("All records have a directly supported deterioration mapping.")
    else:
        st.warning(
            "The deterioration model is not ready for final use. Records with "
            "combined span types or category/span mismatches require a documented "
            "mapping rule. No source value has been silently changed."
        )

    st.subheader("Record Readiness")
    readiness = pd.DataFrame(
        {
            "Status": ["Valid", "Review", "Invalid"],
            "Records": [
                summary["valid_row_count"],
                summary["review_row_count"],
                summary["invalid_row_count"],
            ],
        }
    ).set_index("Status")
    st.bar_chart(readiness)

    st.subheader("Validation Issues")

    if result.issues.empty:
        st.info("No validation issues were detected.")
    else:
        filter_col1, filter_col2 = st.columns(2)
        severity_options = sorted(result.issues["Severity"].dropna().unique().tolist())
        category_options = sorted(result.issues["Category"].dropna().unique().tolist())

        selected_severities = filter_col1.multiselect(
            "Severity",
            options=severity_options,
            default=severity_options,
        )
        selected_categories = filter_col2.multiselect(
            "Issue category",
            options=category_options,
            default=category_options,
        )

        filtered_issues = result.issues[
            result.issues["Severity"].isin(selected_severities)
            & result.issues["Category"].isin(selected_categories)
        ].copy()

        st.dataframe(
            filtered_issues,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source_Row": st.column_config.NumberColumn(
                    "Excel Row",
                    format="%d",
                ),
                "Data_Index": None,
            },
        )

        st.download_button(
            "Download validation issues (CSV)",
            data=result.issues.to_csv(index=False).encode("utf-8-sig"),
            file_name="bridge_data_validation_issues.csv",
            mime="text/csv",
        )

    with st.expander("Column profile", expanded=False):
        st.dataframe(
            result.column_profile,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Missing_Percent": st.column_config.NumberColumn(
                    "Missing %",
                    format="%.2f%%",
                )
            },
        )

    with st.expander("Cleaned data preview", expanded=False):
        preview_columns = [
            "Structure_ID",
            "Bridge_Cat",
            "Hwy_ID",
            "Hwy_Dir",
            "KM",
            "Usage_Code",
            "Unique_Span_Type",
            "Inspection_Year",
            "Years_Passed",
            "Data_Quality_Status",
            "Deterioration_Mapping_Status",
            "Outlier_Columns",
        ]
        st.dataframe(
            result.data[preview_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download cleaned dataset (CSV)",
            data=result.data.to_csv(index=False).encode("utf-8-sig"),
            file_name="bridge_data_cleaned.csv",
            mime="text/csv",
        )
