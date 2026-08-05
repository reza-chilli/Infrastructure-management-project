import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path

def render_communication_results_page(df_processed: pd.DataFrame,) -> None:
    """Render budget scenario analysis based on budget."""

    st.title("Communication of results")
    planSummary = st.session_state.get(
      "fifteen_year_plan_summary",
    )
    detailedPlan = st.session_state.get(
      "fifteen_year_plan_detail",
    )
    if (
        "fifteen_year_plan_summary" not in st.session_state
        or "fifteen_year_plan_detail" not in st.session_state
    ):
      st.warning("Please execute the budget scenarios first.")
      st.stop()
    planSummary = pd.DataFrame(planSummary).rename(columns={
      "Calendar_Year": "year",
      "Annual_Budget": "budget",
      "Nominal_Spent": "spent",
      "Budget_Remaining": "remaining",
      "Funded_Bridges": "funded",
      "Deferred_Due_to_Budget": "deferred",
      "No_Action_Needed": "noaction",
      "Average_BCI_Start": "avgBciStart",
      "Average_BCI_End": "avgBciEnd",
      "Poor_Bridges_Start": "poorStart",
      "Poor_Bridges_End": "poorEnd"
    })
    detailedPlan = pd.DataFrame(detailedPlan).rename(columns={
       "Priority Rank": "pr",
       "Priority Score": "ps",
       "Recommended_Treatment_Code": "rt",
       "Treatment_Name": "rtn",
       "Treatment_Cost": "tc",
       "Decision_Status": "ds",
       "Programmed_Treatment_Code": "pt",
       "Programmed_Treatment_Name": "ptn",
       "Programmed_Cost": "pc",
       "BCI_End_of_Year": "bciEnd",
       "End_Condition_Category": "ecc"
    })
    baseLinePlan = detailedPlan.query("Scenario == 'Baseline Budget'")
    constrainedPlan = detailedPlan.query("Scenario == 'Constrained Budget'")
    PLAN = {
      "baseline": {
         str(year): {
            str(row["Structure_ID"]): {
                column: row[column]
                for column in baseLinePlan.columns
                if column not in ["Calendar_Year", "Structure_ID"]
            }
            for _, row in year_df.iterrows()
        }
        for year, year_df in baseLinePlan.groupby("Calendar_Year")
      },
      "constrained": {
        str(year): {
          str(row["Structure_ID"]): {
              column: row[column]
              for column in constrainedPlan.columns
              if column not in ["Calendar_Year", "Structure_ID"]
          }
          for _, row in year_df.iterrows()
        }
        for year, year_df in constrainedPlan.groupby("Calendar_Year")
      }
    }
    baseLineSummary = planSummary.query("Scenario == 'Baseline Budget'")
    constrainedSummary = planSummary.query("Scenario == 'Constrained Budget'")
    SUMMARY = {
      "baseline": baseLineSummary.to_dict(orient="records"),
      "constrained": constrainedSummary.to_dict(orient="records")
    }
    plan_json = json.dumps(
      PLAN,
      ensure_ascii=False,
      default=str
    )
    corridors = {
      "north": [[31.8974, 54.3675], [31.99, 54.295], [32.045, 54.22], [32.2496, 54.0169], [32.31, 54.018], [32.4, 54.005], [32.47, 53.98], [32.62, 54.01], [32.78, 54.06]], 
      "northwest": [[31.8974, 54.3675], [31.97, 54.15], [32.1, 53.95], [32.35, 53.68], [32.6, 53.4], [32.86, 53.09]], 
      "southwest": [[31.8974, 54.3675], [31.83, 54.29], [31.7554, 54.2033], [31.62, 54.05], [31.51, 53.86], [31.32, 53.56], [31.1257, 53.2795]], 
      "south": [[31.8974, 54.3675], [31.75, 54.4], [31.5919, 54.4327], [31.38, 54.32], [31.15, 54.15], [30.95, 53.98]], 
      "southeast": [[31.8974, 54.3675], [31.8, 54.65], [31.72, 54.95], [31.6035, 55.4083], [31.4, 55.7], [31.2, 56.05]], 
      "east": [[31.8974, 54.3675], [31.55, 54.85], [31.15, 55.1], [30.8722, 55.2847], [30.6, 55.65], [30.407, 55.998], [30.2839, 57.0834]], 
      "ring": [[31.945, 54.37], [31.92, 54.43], [31.87, 54.42], [31.84, 54.37], [31.87, 54.31], [31.92, 54.315], [31.945, 54.37]]
    }
    locations = {
      "B1": { "lat": 31.86821, "lon": 54.41702, "corridor": "ring" },
      "B2": { "lat": 31.92972, "lon": 54.33637, "corridor": "ring" },
      "B3": { "lat": 31.20486, "lon": 54.19055, "corridor": "south" },
      "B4": { "lat": 31.85225, "lon": 54.34549, "corridor": "ring" },
      "B5": { "lat": 30.80569, "lon": 55.37396, "corridor": "east" },
      "B6": { "lat": 31.09749, "lon": 54.10536, "corridor": "south" },
      "B7": { "lat": 31.89898, "lon": 54.36277, "corridor": "northwest" },
      "B8": { "lat": 31.89808, "lon": 54.3723, "corridor": "east" },
      "B9": { "lat": 31.89326, "lon": 54.3675, "corridor": "east" },
      "B10": { "lat": 31.8903, "lon": 54.35934, "corridor": "southwest" },
      "B11": { "lat": 32.47951, "lon": 53.9819, "corridor": "north" },
      "B12": { "lat": 31.32261, "lon": 54.27758, "corridor": "south" },
      "B13": { "lat": 31.92196, "lon": 54.34827, "corridor": "north" },
      "B14": { "lat": 30.52233, "lon": 55.79005, "corridor": "east" },
      "B15": { "lat": 31.44249, "lon": 54.35324, "corridor": "south" },
      "B16": { "lat": 31.86238, "lon": 54.40731, "corridor": "ring" },
      "B17": { "lat": 30.75225, "lon": 55.44567, "corridor": "east" },
      "B18": { "lat": 31.88768, "lon": 54.31177, "corridor": "ring" },
      "B19": { "lat": 31.84978, "lon": 54.38629, "corridor": "ring" },
      "B20": { "lat": 32.6937, "lon": 54.03303, "corridor": "north" },
      "B21": { "lat": 31.02622, "lon": 54.04479, "corridor": "south" },
      "B22": { "lat": 31.8994, "lon": 54.36151, "corridor": "northwest" },
      "B23": { "lat": 31.85305, "lon": 54.39176, "corridor": "ring" },
      "B24": { "lat": 31.237, "lon": 54.21431, "corridor": "south" },
      "B25": { "lat": 32.43694, "lon": 53.99181, "corridor": "north" },
      "B26": { "lat": 31.84089, "lon": 54.36822, "corridor": "ring" },
      "B27": { "lat": 32.13902, "lon": 54.12667, "corridor": "north" },
      "B28": { "lat": 31.92513, "lon": 54.32628, "corridor": "ring" },
      "B29": { "lat": 31.84452, "lon": 54.37753, "corridor": "ring" },
      "B30": { "lat": 30.80452, "lon": 55.37552, "corridor": "east" },
      "B31": { "lat": 32.20255, "lon": 53.83925, "corridor": "northwest" },
      "B32": { "lat": 31.8911, "lon": 54.42799, "corridor": "ring" },
      "B33": { "lat": 31.89215, "lon": 54.42066, "corridor": "ring" },
      "B34": { "lat": 31.75554, "lon": 54.82913, "corridor": "southeast" },
      "B35": { "lat": 31.74953, "lon": 54.82686, "corridor": "southeast" },
      "B36": { "lat": 31.85786, "lon": 54.33429, "corridor": "ring" },
      "B37": { "lat": 31.50223, "lon": 54.38501, "corridor": "south" },
      "B38": { "lat": 31.24596, "lon": 55.96957, "corridor": "southeast" },
      "B39": { "lat": 31.86798, "lon": 54.31404, "corridor": "ring" },
      "B40": { "lat": 32.69618, "lon": 53.28533, "corridor": "northwest" },
      "B41": { "lat": 32.46921, "lon": 53.54649, "corridor": "northwest" },
      "B42": { "lat": 31.94189, "lon": 54.37747, "corridor": "ring" },
      "B43": { "lat": 30.43108, "lon": 55.95457, "corridor": "east" },
      "B44": { "lat": 32.28031, "lon": 53.75526, "corridor": "northwest" },
      "B45": { "lat": 31.58479, "lon": 53.98919, "corridor": "southwest" },
      "B46": { "lat": 32.3767, "lon": 53.65009, "corridor": "northwest" },
      "B47": { "lat": 30.98084, "lon": 55.21247, "corridor": "east" },
      "B48": { "lat": 31.73402, "lon": 54.60015, "corridor": "east" },
      "B49": { "lat": 31.72932, "lon": 54.59521, "corridor": "east" },
      "B50": { "lat": 31.00731, "lon": 54.02871, "corridor": "south" },
      "B51": { "lat": 32.60962, "lon": 54.00792, "corridor": "north" },
      "B52": { "lat": 31.84271, "lon": 54.37452, "corridor": "ring" },
      "B53": { "lat": 31.41077, "lon": 55.68456, "corridor": "southeast" },
      "B54": { "lat": 31.84465, "lon": 54.3607, "corridor": "ring" },
      "B55": { "lat": 31.86314, "lon": 54.32373, "corridor": "ring" },
      "B56": { "lat": 31.06063, "lon": 55.15942, "corridor": "east" },
      "B57": { "lat": 31.85638, "lon": 54.39729, "corridor": "ring" },
      "B58": { "lat": 32.31571, "lon": 53.71704, "corridor": "northwest" },
      "B59": { "lat": 31.55444, "lon": 53.93675, "corridor": "southwest" },
      "B60": { "lat": 31.88225, "lon": 54.39429, "corridor": "east" },
      "B61": { "lat": 31.87698, "lon": 54.39013, "corridor": "east" },
      "B62": { "lat": 31.88163, "lon": 54.39515, "corridor": "east" },
      "B63": { "lat": 31.87629, "lon": 54.39108, "corridor": "east" },
      "B64": { "lat": 31.76447, "lon": 54.55787, "corridor": "east" },
      "B65": { "lat": 31.75978, "lon": 54.5529, "corridor": "east" },
      "B66": { "lat": 32.03603, "lon": 54.04841, "corridor": "northwest" },
      "B67": { "lat": 32.02632, "lon": 54.06336, "corridor": "northwest" },
      "B68": { "lat": 31.53329, "lon": 54.40153, "corridor": "south" },
      "B69": { "lat": 32.01998, "lon": 54.07311, "corridor": "northwest" },
      "B70": { "lat": 32.01748, "lon": 54.07696, "corridor": "northwest" },
      "B71": { "lat": 31.79582, "lon": 54.65327, "corridor": "southeast" },
      "B72": { "lat": 31.52893, "lon": 53.8927, "corridor": "southwest" },
      "B73": { "lat": 31.57182, "lon": 53.96678, "corridor": "southwest" },
      "B74": { "lat": 31.85182, "lon": 54.3897, "corridor": "ring" },
      "B75": { "lat": 32.28921, "lon": 54.01762, "corridor": "north" },
      "B76": { "lat": 32.11059, "lon": 53.93856, "corridor": "northwest" },
      "B77": { "lat": 31.73028, "lon": 54.92383, "corridor": "southeast" },
      "B78": { "lat": 31.85348, "lon": 54.39247, "corridor": "ring" },
      "B79": { "lat": 31.8882, "lon": 54.42741, "corridor": "ring" },
      "B80": { "lat": 31.88927, "lon": 54.42009, "corridor": "ring" },
      "B81": { "lat": 31.68692, "lon": 54.66556, "corridor": "east" },
      "B82": { "lat": 31.6964, "lon": 54.64093, "corridor": "east" },
      "B83": { "lat": 31.22238, "lon": 54.2035, "corridor": "south" },
      "B84": { "lat": 30.50298, "lon": 55.82493, "corridor": "east" },
      "B85": { "lat": 31.71427, "lon": 54.97254, "corridor": "southeast" },
      "B86": { "lat": 31.69513, "lon": 54.65417, "corridor": "east" },
      "B87": { "lat": 31.70464, "lon": 54.62948, "corridor": "east" },
      "B88": { "lat": 32.15043, "lon": 53.89554, "corridor": "northwest" },
      "B89": { "lat": 32.69065, "lon": 54.03208, "corridor": "north" },
      "B90": { "lat": 31.47447, "lon": 55.59326, "corridor": "southeast" },
      "B91": { "lat": 31.44059, "lon": 55.64181, "corridor": "southeast" },
      "B92": { "lat": 32.11427, "lon": 53.93459, "corridor": "northwest" },
      "B93": { "lat": 31.33521, "lon": 55.81339, "corridor": "southeast" },
      "B94": { "lat": 31.75753, "lon": 54.5675, "corridor": "east" },
      "B95": { "lat": 31.75278, "lon": 54.56262, "corridor": "east" },
      "B96": { "lat": 32.41537, "lon": 54.00341, "corridor": "north" },
      "B97": { "lat": 31.2608, "lon": 55.94359, "corridor": "southeast" },
      "B98": { "lat": 31.20908, "lon": 55.06726, "corridor": "east" },
      "B99": { "lat": 31.2075, "lon": 55.06825, "corridor": "east" },
      "B100": { "lat": 31.20478, "lon": 55.06158, "corridor": "east" },
      "B101": { "lat": 31.20002, "lon": 55.06456, "corridor": "east" },
      "B102": { "lat": 31.19726, "lon": 55.07464, "corridor": "east" },
      "B103": { "lat": 31.19447, "lon": 55.06803, "corridor": "east" },
      "B104": { "lat": 31.18262, "lon": 55.07544, "corridor": "east" },
      "B105": { "lat": 30.6855, "lon": 55.53526, "corridor": "east" },
      "B106": { "lat": 31.94328, "lon": 54.37413, "corridor": "ring" },
      "B107": { "lat": 31.38013, "lon": 54.32413, "corridor": "south" },
      "B108": { "lat": 31.38275, "lon": 54.31741, "corridor": "south" },
      "B109": { "lat": 31.88199, "lon": 54.38316, "corridor": "east" },
      "B110": { "lat": 31.88896, "lon": 54.38211, "corridor": "southeast" },
      "B111": { "lat": 31.84349, "lon": 54.37033, "corridor": "ring" },
      "B112": { "lat": 31.88676, "lon": 54.38849, "corridor": "southeast" },
      "B113": { "lat": 31.93017, "lon": 54.34524, "corridor": "ring" },
      "B114": { "lat": 31.14274, "lon": 54.13927, "corridor": "south" },
      "B115": { "lat": 31.37741, "lon": 53.64445, "corridor": "southwest" },
      "B116": { "lat": 31.91313, "lon": 54.43239, "corridor": "ring" },
      "B117": { "lat": 31.91438, "lon": 54.42511, "corridor": "ring" },
      "B118": { "lat": 31.93711, "lon": 54.25867, "corridor": "northwest" },
      "B119": { "lat": 31.35292, "lon": 54.96899, "corridor": "east" },
      "B120": { "lat": 31.84877, "lon": 54.35246, "corridor": "ring" },
      "B121": { "lat": 31.60042, "lon": 54.77424, "corridor": "east" },
      "B122": { "lat": 31.60548, "lon": 54.76721, "corridor": "east" },
      "B123": { "lat": 31.8595, "lon": 54.48729, "corridor": "southeast" },
      "B124": { "lat": 31.85363, "lon": 54.48458, "corridor": "southeast" },
      "B125": { "lat": 31.85438, "lon": 54.50216, "corridor": "southeast" },
      "B126": { "lat": 31.8485, "lon": 54.49946, "corridor": "southeast" },
      "B127": { "lat": 31.8485, "lon": 54.49946, "corridor": "southeast" },
      "B128": { "lat": 31.84346, "lon": 54.51408, "corridor": "southeast" },
      "B129": { "lat": 31.46948, "lon": 54.89613, "corridor": "east" },
      "B130": { "lat": 31.54512, "lon": 54.40782, "corridor": "south" },
      "B131": { "lat": 31.70044, "lon": 54.64679, "corridor": "east" },
      "B132": { "lat": 31.7003, "lon": 54.64699, "corridor": "east" },
      "B133": { "lat": 30.4035, "lon": 56.00084, "corridor": "east" },
      "B134": { "lat": 31.49352, "lon": 54.88111, "corridor": "east" },
      "B135": { "lat": 31.84896, "lon": 54.35207, "corridor": "ring" },
      "B136": { "lat": 31.83792, "lon": 54.38062, "corridor": "south" },
      "B137": { "lat": 31.81771, "lon": 54.6085, "corridor": "southeast" },
      "B138": { "lat": 31.81187, "lon": 54.6057, "corridor": "southeast" },
      "B139": { "lat": 31.56966, "lon": 54.81697, "corridor": "east" },
      "B140": { "lat": 32.6018, "lon": 53.39786, "corridor": "northwest" },
      "B141": { "lat": 31.57774, "lon": 54.80574, "corridor": "east" },
      "B142": { "lat": 31.60336, "lon": 54.77016, "corridor": "east" },
      "B143": { "lat": 31.8544, "lon": 54.34119, "corridor": "ring" },
      "B144": { "lat": 31.85103, "lon": 54.38838, "corridor": "ring" },
      "B145": { "lat": 31.87338, "lon": 54.33469, "corridor": "southwest" },
      "B146": { "lat": 31.33489, "lon": 54.98026, "corridor": "east" },
      "B147": { "lat": 31.85596, "lon": 54.33807, "corridor": "ring" },
      "B148": { "lat": 31.39946, "lon": 54.33035, "corridor": "south" },
      "B149": { "lat": 31.2125, "lon": 55.05676, "corridor": "east" },
      "B150": { "lat": 31.80265, "lon": 54.65246, "corridor": "southeast" },
      "B151": { "lat": 31.76769, "lon": 54.3961, "corridor": "south" },
      "B152": { "lat": 32.42032, "lon": 53.60124, "corridor": "northwest" },
      "B153": { "lat": 30.82075, "lon": 55.35375, "corridor": "east" },
      "B154": { "lat": 31.92463, "lon": 54.42732, "corridor": "ring" },
      "B155": { "lat": 31.91906, "lon": 54.42382, "corridor": "ring" },
      "B156": { "lat": 31.91826, "lon": 54.42575, "corridor": "ring" },
      "B157": { "lat": 31.93207, "lon": 54.40945, "corridor": "ring" },
      "B158": { "lat": 31.93066, "lon": 54.39599, "corridor": "ring" },
      "B159": { "lat": 31.96157, "lon": 54.16511, "corridor": "northwest" },
      "B160": { "lat": 31.92395, "lon": 54.42895, "corridor": "ring" },
      "B161": { "lat": 31.91838, "lon": 54.42546, "corridor": "ring" }
    }
    bridges_df = df_processed.rename(columns={
      "Structure_ID": "id",
      "Hwy_ID": "hwy_id",
      "Hwy_Dir": "hwy_dir",
      "KM": "km",
      "Bridge_Cat": "cat",
      "First_Year_In_Service": "first_year",
      "Replacement_Cost": "replacement_cost",
      "No_of_Spans": "spans",
      "Nominal_Bridge_Ln": "length_m",
      "Traffic_Volume": "traffic",
      "BCI": "bci_now",
      "Bridge_condition_Cat": "cond_cat_now",
      "Priority Rank": "priority_rank_now"
    })
    bridges = {}

    for _, row in bridges_df.iterrows():
      bridge_id = row["id"]
      bridges[bridge_id] = {
        "id": bridge_id,
        "hwy_id": row["hwy_id"],
        "hwy_dir": row["hwy_dir"],
        "km": row["km"],
        "cat": row["cat"],
        "first_year": row["first_year"],
        "replacement_cost": row["replacement_cost"],
        "spans": row["spans"],
        "length_m": row["length_m"],
        "traffic": row["traffic"],
        "bci_now": row["bci_now"],
        "priority_rank_now": row["priority_rank_now"],
        "lat": locations.get(bridge_id, {}).get("lat"),
        "lon": locations.get(bridge_id, {}).get("lon"),
        "corridor": locations.get(bridge_id, {}).get("corridor")
    }
    summary_json = json.dumps(
      SUMMARY,
      ensure_ascii=False,
      default=str
    )
    bridges_json = json.dumps(
      bridges,
      ensure_ascii=False,
      default=str
    )
    corridors_json = json.dumps(
      corridors,
      ensure_ascii=False,
      default=str
    )
    htmlCode = f"""
      <!DOCTYPE html>
      <html lang="fa" dir="rtl">
      <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>شبکه پل‌های استان یزد | برنامه ۱۵ ساله مدیریت دارایی</title>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
      <style>
        :root{{
          --bg-0:#11151a;
          --bg-1:#171c22;
          --bg-2:#1f262e;
          --bg-3:#28313b;
          --line:#33404b;
          --text-0:#eef2f5;
          --text-1:#aab6c0;
          --text-2:#748393;
          --clay:#c17a4f;
          --clay-bright:#e0925f;
          --clay-dim:#7a4e34;
          --good:#3fb27f;
          --fair:#e0a72e;
          --poor:#df5b4f;
          --shadow: 0 8px 28px rgba(0,0,0,.45);
        }}
        *{{box-sizing:border-box;}}
        html,body{{height:100%;}}
        body{{
          margin:0;
          font-family:'Vazirmatn', 'Tahoma', sans-serif;
          background:var(--bg-0);
          color:var(--text-0);
          overflow:hidden;
        }}

        #app{{
          display:grid;
          grid-template-columns: 1fr 400px;
          height:100vh;
          width:100vw;
        }}
        #map{{
          height:100%;
          width:100%;
          background:#0c1013;
        }}
        #sidebar{{
          background:var(--bg-1);
          border-left:1px solid var(--line);
          height:100vh;
          overflow-y:auto;
          padding:0 0 28px 0;
          position:relative;
        }}
        #sidebar::-webkit-scrollbar{{width:8px;}}
        #sidebar::-webkit-scrollbar-thumb{{background:var(--bg-3); border-radius:4px;}}

        .brand{{
          padding:22px 22px 16px 22px;
          border-bottom:1px solid var(--line);
          position:sticky; top:0; background:var(--bg-1); z-index:5;
        }}
        .brand .eyebrow{{
          font-size:11px; letter-spacing:.14em; color:var(--clay-bright);
          text-transform:uppercase; font-weight:700; margin-bottom:6px;
        }}
        .brand h1{{
          font-size:19px; margin:0 0 4px 0; font-weight:800; line-height:1.4;
        }}
        .brand .sub{{ font-size:12.5px; color:var(--text-1); line-height:1.6; }}

        .panel{{
          padding:18px 22px;
          border-bottom:1px solid var(--line);
        }}
        .panel h2{{
          font-size:12px; font-weight:700; letter-spacing:.04em; color:var(--text-1);
          text-transform:uppercase; margin:0 0 12px 0; display:flex; align-items:center; gap:8px;
        }}
        .panel h2::before{{
          content:""; width:3px; height:12px; background:var(--clay); display:inline-block; border-radius:2px;
        }}

        /* Year slider */
        .year-row{{ display:flex; align-items:baseline; justify-content:space-between; margin-bottom:10px;}}
        .year-big{{ font-size:34px; font-weight:700; color:var(--clay-bright); direction:ltr;}}
        .year-tag{{ font-size:11px; color:var(--text-2); }}
        input[type=range]{{
          -webkit-appearance:none; width:100%; height:4px; border-radius:2px;
          background:var(--bg-3); outline:none; margin:8px 0 6px 0;
        }}
        input[type=range]::-webkit-slider-thumb{{
          -webkit-appearance:none; width:16px; height:16px; border-radius:50%;
          background:var(--clay-bright); border:3px solid var(--bg-1); box-shadow:0 0 0 1px var(--clay);
          cursor:pointer; margin-top:-6px;
        }}
        input[type=range]::-webkit-slider-runnable-track{{ height:4px; border-radius:2px; background:var(--bg-3);}}
        .year-scale{{ display:flex; justify-content:space-between; font-size:10px; color:var(--text-2);}}

        .seg{{
          display:flex; background:var(--bg-2); border-radius:9px; padding:3px; gap:3px; border:1px solid var(--line);
        }}
        .seg button{{
          flex:1; border:none; background:transparent; color:var(--text-1); padding:8px 6px;
          font-family:inherit; font-size:12px; font-weight:600; border-radius:7px; cursor:pointer;
          transition:.15s;
        }}
        .seg button.active{{ background:var(--clay); color:#1a1006; }}
        .seg button:not(.active):hover{{ color:var(--text-0); }}

        .toggle-row{{
          display:flex; align-items:center; justify-content:space-between;
          padding:9px 0; border-bottom:1px dashed var(--line);
        }}
        .toggle-row:last-child{{ border-bottom:none; }}
        .toggle-row .lbl{{ font-size:13px; font-weight:600; }}
        .toggle-row .desc{{ font-size:11px; color:var(--text-2); margin-top:2px; }}
        .switch{{ position:relative; width:38px; height:21px; flex:none; }}
        .switch input{{ opacity:0; width:0; height:0; }}
        .slider-el{{
          position:absolute; cursor:pointer; inset:0; background:var(--bg-3);
          border-radius:20px; transition:.2s; border:1px solid var(--line);
        }}
        .slider-el::before{{
          content:""; position:absolute; height:15px; width:15px; right:2px; top:2px;
          background:var(--text-1); border-radius:50%; transition:.2s;
        }}
        .switch input:checked + .slider-el{{ background:var(--clay-dim); border-color:var(--clay); }}
        .switch input:checked + .slider-el::before{{ background:var(--clay-bright); transform:translateX(-17px); }}

        /* KPI cards */
        .kpi-grid{{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
        .kpi{{
          background:var(--bg-2); border:1px solid var(--line); border-radius:10px; padding:10px 12px;
        }}
        .kpi .v{{ font-size:19px; font-weight:700; direction:ltr; }}
        .kpi .l{{ font-size:10.5px; color:var(--text-2); margin-top:2px; }}
        .kpi.warn .v{{ color:var(--poor); }}
        .kpi.good .v{{ color:var(--good); }}
        .kpi.clay .v{{ color:var(--clay-bright); }}

        /* budget bar */
        .budget-wrap{{ margin-top:12px; }}
        .budget-bar{{
          height:10px; border-radius:6px; background:var(--bg-3); overflow:hidden; border:1px solid var(--line);
          position:relative;
        }}
        .budget-bar .fill{{ height:100%; background:linear-gradient(90deg,var(--clay-dim),var(--clay-bright)); }}
        .budget-legend{{ display:flex; justify-content:space-between; font-size:10.5px; color:var(--text-2); margin-top:5px;}}

        svg.chart{{ width:100%; height:auto; display:block; }}
        .chart-caption{{ font-size:10.5px; color:var(--text-2); margin-top:6px; line-height:1.6; }}
        .chart-legend{{ display:flex; gap:14px; font-size:10.5px; color:var(--text-1); margin-top:4px;}}
        .chart-legend span{{ display:inline-flex; align-items:center; gap:5px; }}
        .chart-legend i{{ width:10px; height:3px; border-radius:2px; display:inline-block; }}

        /* legend */
        .legend-row{{ display:flex; align-items:center; gap:9px; font-size:12px; padding:5px 0; }}
        .dot{{ width:12px; height:12px; border-radius:50%; flex:none; border:2px solid rgba(255,255,255,.15); }}
        .ring{{ width:14px;height:14px;border-radius:50%;border:2.5px dashed; flex:none; }}

        /* map popup */
        .leaflet-popup-content-wrapper{{
          background:var(--bg-1); color:var(--text-0); border-radius:12px; border:1px solid var(--line); box-shadow:var(--shadow);
        }}
        .leaflet-popup-tip{{ background:var(--bg-1); }}
        .leaflet-popup-content{{ margin:14px 16px; font-family:'Vazirmatn'; direction:rtl; width:270px !important; }}
        .pop-title{{ font-size:15px; font-weight:800; color:var(--clay-bright); margin-bottom:2px;}}
        .pop-sub{{ font-size:11px; color:var(--text-2); margin-bottom:10px; direction:ltr; text-align:right;}}
        .pop-grid{{ display:grid; grid-template-columns:1fr 1fr; gap:6px 10px; font-size:12px; margin-bottom:8px;}}
        .pop-grid .k{{ color:var(--text-2); font-size:10.5px; }}
        .pop-grid .v{{ font-weight:700; }}
        .pop-badge{{
          display:inline-block; padding:4px 9px; border-radius:20px; font-size:11px; font-weight:700; margin-top:2px;
        }}
        .leaflet-container{{ background:#0c1013; font-family:'Vazirmatn'; }}
        .leaflet-control-zoom a{{ background:var(--bg-2) !important; color:var(--text-0) !important; border-color:var(--line) !important; }}
        .leaflet-control-attribution{{ background:rgba(23,28,34,.8) !important; color:var(--text-2) !important; }}
        .leaflet-control-attribution a{{ color:var(--text-1) !important; }}

        .rank-badge{{
          background:var(--clay); color:#1a1006; font-weight:700; font-size:10px;
          border-radius:50%; width:19px; height:19px; display:flex; align-items:center; justify-content:center;
          border:2px solid var(--bg-0); box-shadow:0 1px 4px rgba(0,0,0,.5);
        }}

        .footer-note{{
          padding:16px 22px; font-size:10.5px; color:var(--text-2); line-height:1.9; border-top:1px solid var(--line);
        }}

        #map-title{{
          position:absolute; top:16px; right:16px; z-index:1000;
          background:rgba(23,28,34,.88); border:1px solid var(--line); border-radius:12px;
          padding:10px 16px; box-shadow:var(--shadow); backdrop-filter:blur(6px);
          font-size:12.5px; color:var(--text-1); max-width:340px;
        }}
        #map-title b{{ color:var(--text-0); font-size:13.5px; }}

        @media (max-width: 900px){{
          #app{{ grid-template-columns: 1fr; grid-template-rows: 55vh 45vh; }}
          #sidebar{{ border-left:none; border-top:1px solid var(--line); height:45vh; }}
        }}
      </style>
      </head>
      <body>
      <div id="app">
        <div id="map">
          <div id="map-title">
            <b>شبکه پل‌های استان یزد</b><br>
            نمای <span id="titleMode">وضعیت کلی شبکه</span> — سال <span id="titleYear" class="mono"></span>
          </div>
        </div>

        <div id="sidebar">
          <div class="brand">
            <div class="eyebrow">سامانه پایش دارایی — پل‌های استان یزد</div>
            <h1>برنامه ۱۵ ساله مدیریت پل‌ها</h1>
            <div class="sub">۱۶۱ سازه پل روی محورهای اصلی استان یزد؛ نمایش وضعیت، اولویت‌بندی و سناریوهای بودجه‌ای سال‌به‌سال.</div>
          </div>

          <div class="panel">
            <h2>سال برنامه</h2>
            <div class="year-row">
              <div class="year-big mono" id="yearLabel">2026</div>
              <div class="year-tag" id="yearRelTag">سال پایه (وضعیت فعلی شبکه)</div>
            </div>
            <input type="range" id="yearSlider" min="2026" max="2040" step="1" value="2026">
            <div class="year-scale mono"><span>2026</span><span>2033</span><span>2040</span></div>
          </div>

          <div class="panel">
            <h2>سناریوی مالی</h2>
            <div class="seg" id="scenarioSeg">
              <button data-v="baseline" class="active">بودجه پایه</button>
              <button data-v="constrained">بودجه محدود (٪۲۰-)</button>
            </div>
          </div>

          <div class="panel">
            <h2>لایه‌های نقشه</h2>
            <div class="toggle-row">
              <div>
                <div class="lbl">فقط پل‌های دارای اقدام</div>
                <div class="desc">فیلتر به پل‌هایی که در سال انتخابی، طبق سناریوی مالی، اقدام برنامه‌ریزی‌شده دارند</div>
              </div>
              <label class="switch"><input type="checkbox" id="filterAction"><span class="slider-el"></span></label>
            </div>
            <div class="toggle-row">
              <div>
                <div class="lbl">لایه اولویت‌بندی</div>
                <div class="desc">حلقهٔ رنگی و رتبهٔ اولویت هر پل در سال انتخابی</div>
              </div>
              <label class="switch"><input type="checkbox" id="priorityLayer"><span class="slider-el"></span></label>
            </div>
            <div class="toggle-row">
              <div>
                <div class="lbl">نمایش محور راه‌ها</div>
                <div class="desc">مسیر تقریبی محورهای اصلی که پل‌ها بر روی آن قرار دارند</div>
              </div>
              <label class="switch"><input type="checkbox" id="roadsLayer" checked><span class="slider-el"></span></label>
            </div>
          </div>

          <div class="panel">
            <h2>شاخص‌های سال انتخابی</h2>
            <div class="kpi-grid">
              <div class="kpi clay"><div class="v mono" id="kpiActions">--</div><div class="l">پل دارای اقدام</div></div>
              <div class="kpi warn"><div class="v mono" id="kpiPoor">--</div><div class="l">پل در وضعیت بحرانی (پایان سال)</div></div>
              <div class="kpi good"><div class="v mono" id="kpiBci">--</div><div class="l">میانگین BCI شبکه</div></div>
              <div class="kpi"><div class="v mono" id="kpiDeferred">--</div><div class="l">پل به‌تعویق‌افتاده (کمبود بودجه)</div></div>
            </div>
            <div class="budget-wrap">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-1);margin-bottom:4px;">
                <span>هزینهٔ برنامه‌ریزی‌شده</span><span id="budgetPct" class="mono">--</span>
              </div>
              <div class="budget-bar"><div class="fill" id="budgetFill" style="width:0%"></div></div>
              <div class="budget-legend">
                <span id="budgetSpent">$0</span>
                <span id="budgetTotal">از $0 بودجهٔ سالانه</span>
              </div>
            </div>
          </div>

          <div class="panel">
            <h2>روند ۱۵ ساله شبکه</h2>
            <div id="chartPoor"></div>
            <div class="chart-legend">
              <span><i style="background:var(--clay-bright)"></i>بودجه پایه</span>
              <span><i style="background:var(--text-2)"></i>بودجه محدود</span>
            </div>
            <div class="chart-caption">تعداد پل‌های با وضعیت بحرانی در پایان هر سال، بر اساس هر سناریوی مالی. خط عمودی: سال انتخاب‌شده.</div>
          </div>

          <div class="panel">
            <h2>راهنمای وضعیت سازه</h2>
            <div class="legend-row"><span class="dot" style="background:var(--good)"></span> خوب — BCI ≥ 70</div>
            <div class="legend-row"><span class="dot" style="background:var(--fair)"></span> متوسط — 50 ≤ BCI &lt; 70</div>
            <div class="legend-row"><span class="dot" style="background:var(--poor)"></span> بحرانی — BCI &lt; 50</div>
            <div class="legend-row"><span class="ring" style="border-color:var(--poor)"></span> اولویت اقدام بسیار بالا</div>
            <div class="legend-row"><span class="ring" style="border-color:var(--fair)"></span> اولویت اقدام متوسط</div>
            <div class="legend-row"><span class="ring" style="border-color:var(--good)"></span> اولویت اقدام پایین</div>
            <div class="legend-row">اندازهٔ دایره متناسب با ارزش جایگزینی (بودجه) سازه است.</div>
          </div>

          <div class="footer-note">
            داده پایه از شناسنامهٔ ۱۶۱ پل استان یزد استخراج شده است. مختصات جغرافیایی هر پل بر پایهٔ کد محور و کیلومتراژ آن، به‌صورت تقریبی روی محورهای اصلی واقعی استان (یزد–اردکان–عقدا، یزد–تفت–ابرکوه، یزد–مهریز، یزد–بافق، یزد–عنار–کرمان، یزد–نائین و کمربندی یزد) جانمایی شده و برای نمایش تحلیلی است، نه مختصات GPS ثبت‌شدهٔ میدانی. محاسبات فرسودگی، هزینه و اولویت‌بندی مستقیماً از موتور تحلیل پروژه گرفته شده است.
          </div>
        </div>
      </div>

      <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
      <script>

      const BRIDGES = {bridges_json}
      const PLAN = {plan_json}
      const SUMMARY = {summary_json}
      const CORRIDORS = {corridors_json}

      </script>
      <script>
      (function(){{
        "use strict";

        var COND_COLOR = {{ "Good": "#3fb27f", "Fair": "#e0a72e", "Poor": "#df5b4f" }};
        var COND_FA = {{ "Good": "خوب", "Fair": "متوسط", "Poor": "بحرانی" }};
        var TREAT_FA = {{
          "deferred": "بدون اقدام / به تعویق افتاده",
          "preventive_maintenance": "نگهداری پیشگیرانه",
          "regular_rehabilitation": "بازسازی معمولی",
          "heavy_rehabilitation": "بازسازی سنگین",
          "bridge_replacement": "تعویض/بازسازی کامل پل"
        }};
        var TREAT_COLOR = {{
          "deferred": "#5b6773",
          "preventive_maintenance": "#4f8fe0",
          "regular_rehabilitation": "#9c6fe0",
          "heavy_rehabilitation": "#e08a3f",
          "bridge_replacement": "#c53f3f"
        }};
        var DECISION_FA = {{
          "No Action Needed": "نیازی به اقدام نیست",
          "Deferred Due to Budget": "به دلیل کمبود بودجه به تعویق افتاد",
          "Funded": "دارای بودجهٔ اجرا"
        }};
        var CORRIDOR_FA = {{
          "north": "محور یزد–میبد–اردکان–عقدا",
          "northwest": "محور یزد–نائین",
          "southwest": "محور یزد–تفت–ابرکوه",
          "south": "محور یزد–مهریز",
          "southeast": "محور یزد–بافق",
          "east": "محور یزد–عنار–کرمان",
          "ring": "کمربندی و راه‌های پیرامونی یزد"
        }};

        var state = {{ year: 2026, scenario: "baseline", filterAction: false, priorityLayer: false, roadsLayer: true }};

        var map = L.map('map', {{ zoomControl: true, attributionControl: true }})
          .setView([31.85, 54.55], 8);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 18,
          attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        (function fitToBridges(){{
          var latlngs = Object.keys(BRIDGES).map(function(id){{ return [BRIDGES[id].lat, BRIDGES[id].lon]; }});
          if (latlngs.length){{
            map.fitBounds(L.latLngBounds(latlngs), {{ padding: [30,30] }});
          }}
        }})();

        var roadsGroup = L.layerGroup().addTo(map);
        var bridgesGroup = L.layerGroup().addTo(map);
        var priorityGroup = L.layerGroup().addTo(map);

        // ---- draw road corridors ----
        Object.keys(CORRIDORS).forEach(function(key){{
          var pts = CORRIDORS[key];
          var line = L.polyline(pts, {{
            color: '#c17a4f', weight: 2, opacity: 0.35, dashArray: '2 7'
          }});
          line.bindTooltip(CORRIDOR_FA[key] || key, {{sticky:true}});
          roadsGroup.addLayer(line);
        }});

        function fmtMoney(v){{
          if (v == null || isNaN(v)) return "$0";
          var abs = Math.abs(v);
          if (abs >= 1e9) return "$" + (v/1e9).toFixed(2) + "B";
          if (abs >= 1e6) return "$" + (v/1e6).toFixed(2) + "M";
          if (abs >= 1e3) return "$" + (v/1e3).toFixed(0) + "K";
          return "$" + v.toFixed(0);
        }}

        function radiusForCost(cost){{
          if (!cost || cost <= 0) return 5;
          var r = 4 + Math.log10(cost) * 1.9;
          return Math.max(5, Math.min(r, 15));
        }}

        function priorityColor(rank, total){{
          // rank 1 = most urgent -> red; last -> green
          var t = (rank - 1) / Math.max(total - 1, 1); // 0..1
          // interpolate red -> amber -> green
          var c1 = [223,91,79], c2=[224,167,46], c3=[63,178,127];
          var col;
          if (t < 0.5){{
            var tt = t/0.5;
            col = c1.map(function(v,i){{ return Math.round(v + (c2[i]-v)*tt); }});
          }} else {{
            var tt2 = (t-0.5)/0.5;
            col = c2.map(function(v,i){{ return Math.round(v + (c3[i]-v)*tt2); }});
          }}
          return "rgb(" + col.join(",") + ")";
        }}

        function popupHtml(b, rec){{
          var condColor = COND_COLOR[rec ? rec.ecc : b.cond_cat_now] || "#999";
          var condFa = COND_FA[rec ? rec.ecc : b.cond_cat_now] || "--";
          var treatFa = rec ? (TREAT_FA[rec.pt] || rec.pt) : "--";
          var bci = rec ? rec.bciEnd : b.bci_now;
          var pr = rec ? rec.pr : b.priority_rank_now;
          var cost = rec ? rec.pc : 0;
          var decision = rec ? (DECISION_FA[rec.ds] || rec.ds) : "";
          var html = ''
            + '<div class="pop-title">پل ' + b.id + '</div>'
            + '<div class="pop-sub">' + b.hwy_id + ' &middot; KM ' + b.km + ' &middot; ' + b.cat + '</div>'
            + '<div class="pop-grid">'
            + '<div><div class="k">وضعیت (سال ' + state.year + ')</div><div class="v" style="color:' + condColor + '">' + condFa + '</div></div>'
            + '<div><div class="k">شاخص سازه BCI</div><div class="v mono">' + (bci!=null? bci.toFixed(1): '--') + '</div></div>'
            + '<div><div class="k">رتبهٔ اولویت</div><div class="v mono">#' + (pr!=null?pr:'--') + ' از 161</div></div>'
            + '<div><div class="k">سال بهره‌برداری</div><div class="v mono">' + (b.first_year||'--') + '</div></div>'
            + '<div><div class="k">تردد روزانه</div><div class="v mono">' + (b.traffic!=null? b.traffic.toLocaleString('en-US'):'--') + '</div></div>'
            + '<div><div class="k">ارزش جایگزینی</div><div class="v mono">' + fmtMoney(b.replacement_cost) + '</div></div>'
            + '</div>'
            + '<div style="border-top:1px solid var(--line); margin:8px 0; padding-top:8px;">'
            + '<div class="k" style="font-size:10.5px;color:var(--text-2);">اقدام برنامه‌ریزی‌شده در ' + state.year + '</div>'
            + '<span class="pop-badge" style="background:' + (TREAT_COLOR[rec?rec.pt:'deferred']) + '22; color:' + (TREAT_COLOR[rec?rec.pt:'deferred']) + '; border:1px solid ' + (TREAT_COLOR[rec?rec.pt:'deferred']) + '55;">' + treatFa + '</span>'
            + '<div style="font-size:11px; color:var(--text-1); margin-top:6px;">' + decision + (cost>0 ? ' &middot; هزینه: ' + fmtMoney(cost) : '') + '</div>'
            + '</div>';
          return html;
        }}

        function render(){{
          var year = state.year;
          var scen = state.scenario;
          var yearData = (PLAN[scen] && PLAN[scen][year]) ? PLAN[scen][year] : {{}};
          console.log(PLAN[scen][year])
          document.getElementById('yearLabel').textContent = year;
          document.getElementById('titleYear').textContent = year;
          document.getElementById('yearRelTag').textContent = (year === 2026) ? "سال پایه (وضعیت فعلی شبکه)" : "افق برنامه — سال " + (year-2025) + "ام";
          document.getElementById('titleMode').textContent = state.filterAction ? "پل‌های دارای اقدام" : "وضعیت کلی شبکه";

          bridgesGroup.clearLayers();
          priorityGroup.clearLayers();

          var ids = Object.keys(BRIDGES);
          var totalN = ids.length;

          // sort by priority rank (that year) descending draw order so high priority drawn last (on top)
          ids.sort(function(a,b2){{
            var ra = (yearData[a] ? yearData[a].pr : 999);
            var rb = (yearData[b2] ? yearData[b2].pr : 999);
            return rb - ra;
          }});

          var actionCount = 0, poorCount = 0, deferredCount = 0, bciSum = 0, bciN = 0, costSum = 0;

          ids.forEach(function(id){{
            var b = BRIDGES[id];
            var rec = yearData[id];
            var hasAction = rec && rec.pt !== 'deferred';
            if (rec){{
              if (rec.ecc === 'Poor') poorCount++;
              if (rec.ds === 'Deferred Due to Budget') deferredCount++;
              if (rec.bciEnd != null){{ bciSum += rec.bciEnd; bciN++; }}
              if (hasAction){{ actionCount++; costSum += (rec.pc||0); }}
            }}

            if (state.filterAction && !hasAction) return;

            var condCat = rec ? rec.ecc : b.cond_cat_now;
            var color = COND_COLOR[condCat] || '#888';
            var strokeColor = hasAction ? (TREAT_COLOR[rec.pt] || '#fff') : 'rgba(255,255,255,.25)';
            var costForSize = hasAction ? rec.pc : b.replacement_cost;
            var r = hasAction ? Math.max(radiusForCost(costForSize), 6) : radiusForCost(b.replacement_cost) * 0.7;

            var marker = L.circleMarker([b.lat, b.lon], {{
              radius: r,
              color: strokeColor,
              weight: hasAction ? 2.5 : 1.3,
              fillColor: color,
              fillOpacity: 0.82,
              opacity: 1
            }});
            marker.bindPopup(popupHtml(b, rec), {{maxWidth: 300}});
            marker.bindTooltip(id, {{direction:'top', offset:[0,-r]}});
            bridgesGroup.addLayer(marker);

            if (state.priorityLayer && rec && rec.pr != null){{
              var pcol = priorityColor(rec.pr, totalN);
              var ring = L.circleMarker([b.lat, b.lon], {{
                radius: r + 5,
                color: pcol,
                weight: 2.2,
                dashArray: '3 3',
                fill: false,
                opacity: 0.95
              }});
              priorityGroup.addLayer(ring);
              if (rec.pr <= 15){{
                var label = L.marker([b.lat, b.lon], {{
                  icon: L.divIcon({{
                    className: '',
                    html: '<div class="rank-badge" style="background:' + pcol + '">' + rec.pr + '</div>',
                    iconSize: [19,19],
                    iconAnchor: [9.5 - (r+6), 9.5 + (r+6)]
                  }}),
                  interactive: false
                }});
                priorityGroup.addLayer(label);
              }}
            }}
          }});

          // KPIs
          document.getElementById('kpiActions').textContent = actionCount;
          document.getElementById('kpiPoor').textContent = poorCount;
          document.getElementById('kpiBci').textContent = bciN ? (bciSum/bciN).toFixed(1) : '--';
          document.getElementById('kpiDeferred').textContent = deferredCount;

          var summArr = SUMMARY[scen] || [];
          var summYear = summArr.filter(function(s){{ return s.year === year; }})[0];
          if (summYear){{
            var pct = summYear.budget > 0 ? Math.min(100, (summYear.spent/summYear.budget*100)) : 0;
            document.getElementById('budgetFill').style.width = pct.toFixed(0) + '%';
            document.getElementById('budgetPct').textContent = pct.toFixed(0) + '%';
            document.getElementById('budgetSpent').textContent = fmtMoney(summYear.spent);
            document.getElementById('budgetTotal').textContent = 'از ' + fmtMoney(summYear.budget) + ' بودجهٔ سالانه';
          }}

          drawTrendChart();
        }}

        function drawTrendChart(){{
          var w = 336, h = 130, pad = {{t:8,r:6,b:18,l:26}};
          var years = SUMMARY.baseline.map(function(s){{return s.year;}});
          var maxPoor = Math.max.apply(null, SUMMARY.baseline.concat(SUMMARY.constrained).map(function(s){{return s.poorEnd;}})) || 1;
          var innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;

          function xy(idx, val){{
            var x = pad.l + (idx/(years.length-1)) * innerW;
            var y = pad.t + innerH - (val/maxPoor) * innerH;
            return [x,y];
          }}
          function pathFor(arr){{
            return arr.map(function(s,i){{ var p = xy(i, s.poorEnd); return (i===0?'M':'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }}).join(' ');
          }}

          var selIdx = years.indexOf(state.year);
          var selX = pad.l + (selIdx/(years.length-1)) * innerW;

          var svg = ''
            + '<svg class="chart" viewBox="0 0 ' + w + ' ' + h + '">'
            + '<line x1="' + pad.l + '" y1="' + (pad.t+innerH) + '" x2="' + (w-pad.r) + '" y2="' + (pad.t+innerH) + '" stroke="#33404b" stroke-width="1"/>'
            + '<line x1="' + selX.toFixed(1) + '" y1="' + pad.t + '" x2="' + selX.toFixed(1) + '" y2="' + (pad.t+innerH) + '" stroke="#c17a4f" stroke-width="1.4" stroke-dasharray="3 3"/>'
            + '<path d="' + pathFor(SUMMARY.constrained) + '" fill="none" stroke="#748393" stroke-width="2"/>'
            + '<path d="' + pathFor(SUMMARY.baseline) + '" fill="none" stroke="#e0925f" stroke-width="2.4"/>'
            + '<text x="' + pad.l + '" y="12" fill="#748393" font-size="9">' + maxPoor + '</text>'
            + '<text x="' + pad.l + '" y="' + (pad.t+innerH+3) + '" fill="#748393" font-size="9">0</text>'
            + '<text x="' + (pad.l-2) + '" y="' + (h-2) + '" fill="#748393" font-size="9">' + years[0] + '</text>'
            + '<text x="' + (w-pad.r-24) + '" y="' + (h-2) + '" fill="#748393" font-size="9">' + years[years.length-1] + '</text>'
            + '</svg>';
          document.getElementById('chartPoor').innerHTML = svg;
        }}

        // ---- controls ----
        document.getElementById('yearSlider').addEventListener('input', function(e){{
          state.year = parseInt(e.target.value, 10);
          render();
        }});
        document.querySelectorAll('#scenarioSeg button').forEach(function(btn){{
          btn.addEventListener('click', function(){{
            document.querySelectorAll('#scenarioSeg button').forEach(function(b){{ b.classList.remove('active'); }});
            btn.classList.add('active');
            state.scenario = btn.getAttribute('data-v');
            render();
          }});
        }});
        document.getElementById('filterAction').addEventListener('change', function(e){{
          state.filterAction = e.target.checked;
          render();
        }});
        document.getElementById('priorityLayer').addEventListener('change', function(e){{
          state.priorityLayer = e.target.checked;
          render();
        }});
        document.getElementById('roadsLayer').addEventListener('change', function(e){{
          state.roadsLayer = e.target.checked;
          if (state.roadsLayer) map.addLayer(roadsGroup); else map.removeLayer(roadsGroup);
        }});

        render();
      }})();

      </script>
      </body>
      </html>
    """

    components.html(htmlCode, height=700, scrolling=True)