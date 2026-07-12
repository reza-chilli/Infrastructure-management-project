import numpy as np
import pandas as pd


BRIDGE_TYPES = {
    "Standard": {
        "Timber": ["TP", "TT"],
        "Prestressed": ["SCC", "SM", "SMC", "VS", "VSO"],
        "Precast": ["HC"],
    },
    "Major": {
        "Concrete": {
            "Pre_stressed_girder": [
                "CBC", "DBC", "CBT", "DBT", "FC", "FM", "LF",
                "PJ", "PM", "PO", "PQ", "RD", "RM", "VF",
            ],
            "Pre_cast_girder": ["PE"],
            "Cast_in_place": ["CA", "CF", "CS", "CT", "CV", "CX"],
        },
        "Steel": {
            "Beam": ["FR", "WG", "RB", "RG"],
            "Truss": ["TH"],
        },
    },
}


def calculate_decay(initial_rating, bridge_type, unique_span_type, years):
    if pd.isna(initial_rating) or pd.isna(bridge_type) or pd.isna(years):
        return initial_rating

    current_rating = initial_rating
    bridge_type = bridge_type.strip()

    for _ in range(int(years)):
        rate = 0

        if bridge_type == "STD":
            if current_rating >= 88:
                rate = 2.7
            elif current_rating < 88 and current_rating >= 77:
                rate = 1.4
            elif current_rating < 77 and current_rating >= 66:
                rate = 1.7
            elif current_rating < 66 and current_rating >= 55:
                rate = 1.3
            elif current_rating < 55 and current_rating >= 44:
                rate = 1.3
            elif current_rating < 44 and current_rating >= 33:
                rate = 2.1
            elif current_rating < 33 and current_rating >= 22:
                rate = 3.1
            elif current_rating < 22 and current_rating >= 11:
                rate = 2.8

        elif bridge_type == "MAJ":
            if unique_span_type in BRIDGE_TYPES["Major"]["Concrete"]["Pre_stressed_girder"]:
                if current_rating >= 88:
                    rate = 2.2
                elif current_rating < 88 and current_rating >= 77:
                    rate = 1.5
                elif current_rating < 77 and current_rating >= 66:
                    rate = 1.3
                elif current_rating < 66 and current_rating >= 55:
                    rate = 1.1
                elif current_rating < 55 and current_rating >= 44:
                    rate = 1.4
                elif current_rating < 44 and current_rating >= 33:
                    rate = 1.6
                elif current_rating < 33 and current_rating >= 22:
                    rate = 2.1
                elif current_rating < 22 and current_rating >= 11:
                    rate = 3.7

            if unique_span_type in BRIDGE_TYPES["Major"]["Concrete"]["Pre_cast_girder"]:
                if current_rating >= 88:
                    rate = 5.4
                elif current_rating < 88 and current_rating >= 77:
                    rate = 1.8
                elif current_rating < 77 and current_rating >= 66:
                    rate = 1.4
                elif current_rating < 66 and current_rating >= 55:
                    rate = 1.1
                elif current_rating < 55 and current_rating >= 44:
                    rate = 1.1
                elif current_rating < 44 and current_rating >= 33:
                    rate = 1.3
                elif current_rating < 33 and current_rating >= 22:
                    rate = 1.9
                elif current_rating < 22 and current_rating >= 11:
                    rate = 3.7

            if unique_span_type in BRIDGE_TYPES["Major"]["Concrete"]["Cast_in_place"]:
                if current_rating >= 88:
                    rate = 4.2
                elif current_rating < 88 and current_rating >= 77:
                    rate = 2.2
                elif current_rating < 77 and current_rating >= 66:
                    rate = 1.2
                elif current_rating < 66 and current_rating >= 55:
                    rate = 1.3
                elif current_rating < 55 and current_rating >= 44:
                    rate = 1.3
                elif current_rating < 44 and current_rating >= 33:
                    rate = 1.2
                elif current_rating < 33 and current_rating >= 22:
                    rate = 1.8
                elif current_rating < 22 and current_rating >= 11:
                    rate = 4.7

            if unique_span_type in BRIDGE_TYPES["Major"]["Steel"]["Beam"]:
                if current_rating >= 88:
                    rate = 2.6
                elif current_rating < 88 and current_rating >= 77:
                    rate = 1.9
                elif current_rating < 77 and current_rating >= 66:
                    rate = 1.1
                elif current_rating < 66 and current_rating >= 55:
                    rate = 1.4
                elif current_rating < 55 and current_rating >= 44:
                    rate = 1.1
                elif current_rating < 44 and current_rating >= 33:
                    rate = 1.7
                elif current_rating < 33 and current_rating >= 22:
                    rate = 2.1
                elif current_rating < 22 and current_rating >= 11:
                    rate = 2.4

            if unique_span_type in BRIDGE_TYPES["Major"]["Steel"]["Truss"]:
                if current_rating >= 88:
                    rate = 3.6
                elif current_rating < 88 and current_rating >= 77:
                    rate = 3.2
                elif current_rating < 77 and current_rating >= 66:
                    rate = 1.2
                elif current_rating < 66 and current_rating >= 55:
                    rate = 1.4
                elif current_rating < 55 and current_rating >= 44:
                    rate = 1.5
                elif current_rating < 44 and current_rating >= 33:
                    rate = 1.8
                elif current_rating < 33 and current_rating >= 22:
                    rate = 2.7
                elif current_rating < 22 and current_rating >= 11:
                    rate = 7.8

        current_rating -= rate

        if current_rating < 0:
            current_rating = 0
            break

    return round(current_rating, 2)


def normalize(series):
    return ((series - series.min()) / (series.max() - series.min())) * 100


def run_all_calculations(df: pd.DataFrame, current_year: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_processed = df.copy()

    df_processed["current_Cond_Rat_Deck"] = df_processed.apply(
        lambda row: calculate_decay(
            int(row["Cond_Rat_Deck"]),
            row["Bridge_Cat"],
            row["Unique_Span_Type"],
            int(row["Years_Passed"]),
        ),
        axis=1,
    )

    df_processed["current_Cond_Rat_Super"] = df_processed.apply(
        lambda row: calculate_decay(
            int(row["Cond_Rat_Super"]),
            row["Bridge_Cat"],
            row["Unique_Span_Type"],
            int(row["Years_Passed"]),
        ),
        axis=1,
    )

    df_processed["current_Cond_Rat_Sub"] = df_processed.apply(
        lambda row: calculate_decay(
            int(row["Cond_Rat_Sub"]),
            row["Bridge_Cat"],
            row["Unique_Span_Type"],
            int(row["Years_Passed"]),
        ),
        axis=1,
    )

    bridge_deck_weight = 0.3
    bridge_super_structure_weight = 0.35
    bridge_sub_structure_weight = 0.35

    df_processed["BCI"] = (
        bridge_deck_weight * df_processed["current_Cond_Rat_Deck"]
        + bridge_super_structure_weight * df_processed["current_Cond_Rat_Super"]
        + bridge_sub_structure_weight * df_processed["current_Cond_Rat_Sub"]
    )

    summary = pd.DataFrame(
        {
            "Type": df_processed.dtypes,
            "Missing": df_processed.isna().sum(),
            "Missing %": (df_processed.isna().sum() / len(df_processed) * 100).round(2),
            "Unique": df_processed.nunique(),
        }
    )

    print('this is summary', summary)

    df_processed["Age"] = current_year - df_processed["First_Year_In_Service"]

    df_processed["Condition"] = (
        df_processed["Cond_Rat_Deck"]
        + df_processed["Cond_Rat_Super"]
        + df_processed["Cond_Rat_Sub"]
    ) / 3

    df_processed["Condition_Score"] = normalize(100 - df_processed["Condition"])
    df_processed["Age_Score"] = normalize(df_processed["Age"])
    df_processed["Traffic_Score"] = normalize(df_processed["Traffic_Volume"])
    df_processed["Cost_Score"] = normalize(df_processed["Replacement_Cost"])

    df_processed["Priority Score"] = (
        0.40 * df_processed["Condition_Score"]
        + 0.30 * df_processed["Traffic_Score"]
        + 0.20 * df_processed["Age_Score"]
        + 0.10 * df_processed["Cost_Score"]
    )

    top10 = (
        df_processed.sort_values(
            "Priority Score",
            ascending=False,
        )
        .head(10)
    )

    df_processed["Bridge_condition_Cat"] = np.where(
        df_processed["BCI"] >= 80,
        "Good",
        np.where(
            df_processed["BCI"] >= 50,
            "Fair",
            "Poor",
        ),
    )

    lowest_bci = df_processed.sort_values("BCI").head(20)

    kpiCardInfo = {
        'totalBridgeCount': 0,
        'totalCost': 0,
        'averageAge': 0,
        'averageConditionRating': 0,
        'totalDailyTraffic': 0
    }
    kpiCardInfo['totalBridgeCount'] = df_processed.shape[0]
    kpiCardInfo['totalCost'] = df_processed['Replacement_Cost'].sum()
    kpiCardInfo['averageAge'] = df_processed['Age'].sum() / kpiCardInfo['totalBridgeCount']
    kpiCardInfo['averageConditionRating'] = df_processed["Condition"].sum() / kpiCardInfo['totalBridgeCount']
    kpiCardInfo['totalDailyTraffic'] = df_processed['Traffic_Volume'].sum()

    return df_processed, summary, top10, lowest_bci, kpiCardInfo
