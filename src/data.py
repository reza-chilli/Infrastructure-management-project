import numpy as np
import pandas as pd
from datetime import date


# --------------------------------------------------
# Constants
# --------------------------------------------------
EXCEL_FILE_PATH = "../ToR Structures_Data_Updated- bahman 1405.xlsx"

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

CONDITION_COLUMNS = ["Cond_Rat_Deck", "Cond_Rat_Super", "Cond_Rat_Sub"]


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def get_current_year():
    # Return current year
    return date.today().year


def load_bridge_data(file_path: str) -> pd.DataFrame:
    df_raw = pd.read_excel(
        file_path,
        skiprows=2,
        header=None,
        sheet_name="Bridge Data"
    )

    df_trim = df_raw.replace(r"^\s*$", np.nan, regex=True)
    df_trim.columns = COLUMN_NAMES

    return df_trim


def preprocess_bridge_data(df: pd.DataFrame, current_year: int | None = None) -> pd.DataFrame:
    
    # Apply the same preprocessing steps from Analysis.py:
    # - extract inspection year
    # - compute Years_Passed
    # - convert condition columns to numeric
    # - strip Unique_Span_Type
    
    if current_year is None:
        current_year = get_current_year()

    df_trim = df.copy()

    df_trim["Insp_Year"] = pd.to_numeric(
        df_trim["Insp_Date"].astype(str).str.split("-").str[-1],
        errors="coerce"
    )

    df_trim["Years_Passed"] = current_year - df_trim["Insp_Year"]

    for col in CONDITION_COLUMNS:
        df_trim[col] = pd.to_numeric(df_trim[col], errors="coerce")

    df_trim["Unique_Span_Type"] = df_trim["Unique_Span_Type"].astype(str).str.strip()

    return df_trim


def load_and_preprocess_data(file_path: str = EXCEL_FILE_PATH) -> pd.DataFrame:
    # Main entry point for app.py.
    # Loads Excel data and applies preprocessing in the same order as Analysis.py.
    
    current_year = get_current_year()
    df = load_bridge_data(file_path)
    df = preprocess_bridge_data(df, current_year=current_year)
    return df
