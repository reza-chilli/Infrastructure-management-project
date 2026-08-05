import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path

def render_communication_results_page(df_processed: pd.DataFrame,) -> None:
    """Render budget scenario analysis based on budget."""

    st.title("Communication of results")
    annualBudgetSettings = st.session_state.get(
          "fifteen_year_plan_settings",
        )
    detailedPlan = st.session_state.get(
      "fifteen_year_plan_detail",
    )
    if (
        "fifteen_year_plan_settings" not in st.session_state
        or "fifteen_year_plan_detail" not in st.session_state
    ):
      st.warning("Please execute the budget scenarios first.")
      st.stop()
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
    print(df_processed.columns.tolist())
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
    summary = {
      "baseline": [
        {"year": 2026, "budget": 254200000.0, "spent": 254113150.0, "remaining": 86850.0, "funded": 22, "deferred": 139, "noaction": 0, "avgBciStart": 42.0, "avgBciEnd": 50.3, "poorStart": 135, "poorEnd": 113}, 
        {"year": 2027, "budget": 254200000.0, "spent": 254179842.0, "remaining": 20158.0, "funded": 24, "deferred": 121, "noaction": 16, "avgBciStart": 48.6, "avgBciEnd": 56.2, "poorStart": 125, "poorEnd": 101}, 
        {"year": 2028, "budget": 254200000.0, "spent": 254152289.0, "remaining": 47711.0, "funded": 33, "deferred": 99, "noaction": 29, "avgBciStart": 54.3, "avgBciEnd": 65.5, "poorStart": 107, "poorEnd": 75}, 
        {"year": 2029, "budget": 254200000.0, "spent": 254145084.0, "remaining": 54916.0, "funded": 20, "deferred": 86, "noaction": 55, "avgBciStart": 63.6, "avgBciEnd": 70.7, "poorStart": 77, "poorEnd": 60}, 
        {"year": 2030, "budget": 254200000.0, "spent": 254138100.0, "remaining": 61900.0, "funded": 29, "deferred": 66, "noaction": 66, "avgBciStart": 68.7, "avgBciEnd": 78.2, "poorStart": 62, "poorEnd": 36}, 
        {"year": 2031, "budget": 254200000.0, "spent": 254198272.0, "remaining": 1728.0, "funded": 39, "deferred": 42, "noaction": 80, "avgBciStart": 76.1, "avgBciEnd": 87.8, "poorStart": 38, "poorEnd": 7}, 
        {"year": 2032, "budget": 254200000.0, "spent": 227253479.0, "remaining": 26946521.0, "funded": 70, "deferred": 0, "noaction": 91, "avgBciStart": 85.6, "avgBciEnd": 91.1, "poorStart": 7, "poorEnd": 0}, 
        {"year": 2033, "budget": 254200000.0, "spent": 92778486.0, "remaining": 161421514.0, "funded": 29, "deferred": 0, "noaction": 132, "avgBciStart": 88.7, "avgBciEnd": 90.0, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2034, "budget": 254200000.0, "spent": 92361562.0, "remaining": 161838438.0, "funded": 36, "deferred": 0, "noaction": 125, "avgBciStart": 87.6, "avgBciEnd": 89.5, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2035, "budget": 254200000.0, "spent": 101247820.0, "remaining": 152952180.0, "funded": 38, "deferred": 0, "noaction": 123, "avgBciStart": 87.2, "avgBciEnd": 89.2, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2036, "budget": 254200000.0, "spent": 116993055.0, "remaining": 137206945.0, "funded": 45, "deferred": 0, "noaction": 116, "avgBciStart": 86.9, "avgBciEnd": 89.4, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2037, "budget": 254200000.0, "spent": 115788973.0, "remaining": 138411027.0, "funded": 42, "deferred": 0, "noaction": 119, "avgBciStart": 87.0, "avgBciEnd": 89.3, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2038, "budget": 254200000.0, "spent": 96558842.0, "remaining": 157641158.0, "funded": 38, "deferred": 0, "noaction": 123, "avgBciStart": 87.1, "avgBciEnd": 89.2, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2039, "budget": 254200000.0, "spent": 118951727.0, "remaining": 135248273.0, "funded": 39, "deferred": 0, "noaction": 122, "avgBciStart": 86.9, "avgBciEnd": 89.0, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2040, "budget": 254200000.0, "spent": 80896610.0, "remaining": 173303390.0, "funded": 41, "deferred": 0, "noaction": 120, "avgBciStart": 86.8, "avgBciEnd": 89.0, "poorStart": 0, "poorEnd": 0}], 
      "constrained": [
        {"year": 2026, "budget": 203360000.0, "spent": 203357098.0, "remaining": 2902.0, "funded": 21, "deferred": 140, "noaction": 0, "avgBciStart": 42.0, "avgBciEnd": 49.8, "poorStart": 135, "poorEnd": 114}, 
        {"year": 2027, "budget": 203360000.0, "spent": 203231864.0, "remaining": 128136.0, "funded": 18, "deferred": 128, "noaction": 15, "avgBciStart": 48.1, "avgBciEnd": 53.9, "poorStart": 126, "poorEnd": 108}, 
        {"year": 2028, "budget": 203360000.0, "spent": 203312651.0, "remaining": 47349.0, "funded": 22, "deferred": 112, "noaction": 27, "avgBciStart": 52.1, "avgBciEnd": 59.7, "poorStart": 114, "poorEnd": 92}, 
        {"year": 2029, "budget": 203360000.0, "spent": 203352232.0, "remaining": 7768.0, "funded": 23, "deferred": 98, "noaction": 40, "avgBciStart": 57.8, "avgBciEnd": 65.9, "poorStart": 94, "poorEnd": 72}, 
        {"year": 2030, "budget": 203360000.0, "spent": 203322576.0, "remaining": 37424.0, "funded": 14, "deferred": 94, "noaction": 53, "avgBciStart": 63.9, "avgBciEnd": 68.4, "poorStart": 74, "poorEnd": 64}, 
        {"year": 2031, "budget": 203360000.0, "spent": 203327361.0, "remaining": 32639.0, "funded": 24, "deferred": 79, "noaction": 58, "avgBciStart": 66.4, "avgBciEnd": 75.2, "poorStart": 67, "poorEnd": 43}, 
        {"year": 2032, "budget": 203360000.0, "spent": 203350833.0, "remaining": 9167.0, "funded": 23, "deferred": 72, "noaction": 66, "avgBciStart": 73.2, "avgBciEnd": 81.0, "poorStart": 43, "poorEnd": 23}, 
        {"year": 2033, "budget": 203360000.0, "spent": 203295625.0, "remaining": 64375.0, "funded": 29, "deferred": 61, "noaction": 71, "avgBciStart": 78.9, "avgBciEnd": 86.7, "poorStart": 23, "poorEnd": 4}, 
        {"year": 2034, "budget": 203360000.0, "spent": 203283511.0, "remaining": 76489.0, "funded": 62, "deferred": 19, "noaction": 80, "avgBciStart": 84.5, "avgBciEnd": 89.1, "poorStart": 4, "poorEnd": 0}, 
        {"year": 2035, "budget": 203360000.0, "spent": 154416392.0, "remaining": 48943608.0, "funded": 61, "deferred": 0, "noaction": 100, "avgBciStart": 86.8, "avgBciEnd": 90.0, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2036, "budget": 203360000.0, "spent": 88376009.0, "remaining": 114983991.0, "funded": 28, "deferred": 0, "noaction": 133, "avgBciStart": 87.7, "avgBciEnd": 89.1, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2037, "budget": 203360000.0, "spent": 153709224.0, "remaining": 49650776.0, "funded": 57, "deferred": 0, "noaction": 104, "avgBciStart": 86.8, "avgBciEnd": 89.8, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2038, "budget": 203360000.0, "spent": 80379857.0, "remaining": 122980143.0, "funded": 35, "deferred": 0, "noaction": 126, "avgBciStart": 87.4, "avgBciEnd": 89.3, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2039, "budget": 203360000.0, "spent": 113158726.0, "remaining": 90201274.0, "funded": 42, "deferred": 0, "noaction": 119, "avgBciStart": 87.0, "avgBciEnd": 89.3, "poorStart": 0, "poorEnd": 0}, 
        {"year": 2040, "budget": 203360000.0, "spent": 92831348.0, "remaining": 110528652.0, "funded": 35, "deferred": 0, "noaction": 126, "avgBciStart": 87.0, "avgBciEnd": 88.9, "poorStart": 0, "poorEnd": 0}]
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

    bridges = {"B1": {"id": "B1", "lat": 31.86821, "lon": 54.41702, "hwy_id": "135A", "hwy_dir": "C", "km": 14.82, "corridor": "ring", "cat": "STD", "first_year": 1975, "replacement_cost": 251124.0, "spans": 1, "length_m": 11.7, "traffic": 15562, "bci_now": 43.3, "cond_cat_now": "Poor", "priority_rank_now": 71}, "B2": {"id": "B2", "lat": 31.92972, "lon": 54.33637, "hwy_id": "231B", "hwy_dir": "C", "km": 23.77, "corridor": "ring", "cat": "MAJ", "first_year": 1978, "replacement_cost": 4463536.0, "spans": 4, "length_m": 251.2, "traffic": 8773, "bci_now": 50.3, "cond_cat_now": "Fair", "priority_rank_now": 116}, "B3": {"id": "B3", "lat": 31.20486, "lon": 54.19055, "hwy_id": "150A", "hwy_dir": "C", "km": 21.3, "corridor": "south", "cat": "MAJ", "first_year": 1959, "replacement_cost": 1019767.0, "spans": 3, "length_m": 83.8, "traffic": 2277, "bci_now": 38.6, "cond_cat_now": "Poor", "priority_rank_now": 124}, "B4": {"id": "B4", "lat": 31.85225, "lon": 54.34549, "hwy_id": "135F", "hwy_dir": "C", "km": 41.79, "corridor": "ring", "cat": "MAJ", "first_year": 1992, "replacement_cost": 670009.0, "spans": 3, "length_m": 51.4, "traffic": 7101, "bci_now": 37.7, "cond_cat_now": "Poor", "priority_rank_now": 94}, "B5": {"id": "B5", "lat": 30.80569, "lon": 55.37396, "hwy_id": "132B", "hwy_dir": "C", "km": 11.9, "corridor": "east", "cat": "MAJ", "first_year": 1958, "replacement_cost": 1282953.0, "spans": 3, "length_m": 58.4, "traffic": 1840, "bci_now": 49.5, "cond_cat_now": "Poor", "priority_rank_now": 157}, "B6": {"id": "B6", "lat": 31.09749, "lon": 54.10536, "hwy_id": "150B", "hwy_dir": "C", "km": 27.29, "corridor": "south", "cat": "MAJ", "first_year": 1960, "replacement_cost": 1189593.0, "spans": 3, "length_m": 57.2, "traffic": 3525, "bci_now": 45.1, "cond_cat_now": "Poor", "priority_rank_now": 144}, "B7": {"id": "B7", "lat": 31.89898, "lon": 54.36277, "hwy_id": "6A", "hwy_dir": "C", "km": 2.83, "corridor": "northwest", "cat": "MAJ", "first_year": 1962, "replacement_cost": 1670413.0, "spans": 2, "length_m": 100.1, "traffic": 19965, "bci_now": 36.2, "cond_cat_now": "Poor", "priority_rank_now": 4}, "B8": {"id": "B8", "lat": 31.89808, "lon": 54.3723, "hwy_id": "75A", "hwy_dir": "R", "km": 1.11, "corridor": "east", "cat": "MAJ", "first_year": 1978, "replacement_cost": 4549104.0, "spans": 4, "length_m": 237.7, "traffic": 12643, "bci_now": 35.7, "cond_cat_now": "Poor", "priority_rank_now": 10}, "B9": {"id": "B9", "lat": 31.89326, "lon": 54.3675, "hwy_id": "75A", "hwy_dir": "L", "km": 1.12, "corridor": "east", "cat": "MAJ", "first_year": 2000, "replacement_cost": 4043724.0, "spans": 4, "length_m": 192.2, "traffic": 6516, "bci_now": 42.5, "cond_cat_now": "Poor", "priority_rank_now": 93}, "B10": {"id": "B10", "lat": 31.8903, "lon": 54.35934, "hwy_id": "9A", "hwy_dir": "C", "km": 1.48, "corridor": "southwest", "cat": "MAJ", "first_year": 1959, "replacement_cost": 3478925.0, "spans": 5, "length_m": 222.3, "traffic": 7778, "bci_now": 55.8, "cond_cat_now": "Fair", "priority_rank_now": 147}, "B11": {"id": "B11", "lat": 32.47951, "lon": 53.9819, "hwy_id": "138C", "hwy_dir": "C", "km": 32.83, "corridor": "north", "cat": "MAJ", "first_year": 1996, "replacement_cost": 352392.0, "spans": 1, "length_m": 16.8, "traffic": 11325, "bci_now": 37.8, "cond_cat_now": "Poor", "priority_rank_now": 64}, "B12": {"id": "B12", "lat": 31.32261, "lon": 54.27758, "hwy_id": "102C", "hwy_dir": "C", "km": 10.52, "corridor": "south", "cat": "MAJ", "first_year": 1983, "replacement_cost": 5511985.0, "spans": 4, "length_m": 247.2, "traffic": 9749, "bci_now": 35.5, "cond_cat_now": "Poor", "priority_rank_now": 17}, "B13": {"id": "B13", "lat": 31.92196, "lon": 54.34827, "hwy_id": "3A", "hwy_dir": "C", "km": 7.05, "corridor": "north", "cat": "STD", "first_year": 1981, "replacement_cost": 802149.0, "spans": 4, "length_m": 51.9, "traffic": 16130, "bci_now": 48.7, "cond_cat_now": "Poor", "priority_rank_now": 98}, "B14": {"id": "B14", "lat": 30.52233, "lon": 55.79005, "hwy_id": "132D", "hwy_dir": "C", "km": 33.5, "corridor": "east", "cat": "MAJ", "first_year": 1904, "replacement_cost": 2857194.0, "spans": 5, "length_m": 319.1, "traffic": 5048, "bci_now": 43.2, "cond_cat_now": "Poor", "priority_rank_now": 115}, "B15": {"id": "B15", "lat": 31.44249, "lon": 54.35324, "hwy_id": "102B", "hwy_dir": "C", "km": 1.15, "corridor": "south", "cat": "MAJ", "first_year": 1956, "replacement_cost": 1146988.0, "spans": 3, "length_m": 112.5, "traffic": 9772, "bci_now": 51.0, "cond_cat_now": "Fair", "priority_rank_now": 138}, "B16": {"id": "B16", "lat": 31.86238, "lon": 54.40731, "hwy_id": "135B", "hwy_dir": "C", "km": 0.01, "corridor": "ring", "cat": "MAJ", "first_year": 1960, "replacement_cost": 1786569.0, "spans": 4, "length_m": 120.2, "traffic": 6628, "bci_now": 31.6, "cond_cat_now": "Poor", "priority_rank_now": 41}, "B17": {"id": "B17", "lat": 30.75225, "lon": 55.44567, "hwy_id": "132B", "hwy_dir": "C", "km": 26.45, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 1684041.0, "spans": 2, "length_m": 91.7, "traffic": 1923, "bci_now": 42.5, "cond_cat_now": "Poor", "priority_rank_now": 135}, "B18": {"id": "B18", "lat": 31.88768, "lon": 54.31177, "hwy_id": "231A", "hwy_dir": "C", "km": 24.44, "corridor": "ring", "cat": "MAJ", "first_year": 1996, "replacement_cost": 689997.0, "spans": 3, "length_m": 42.0, "traffic": 3970, "bci_now": 39.8, "cond_cat_now": "Poor", "priority_rank_now": 122}, "B19": {"id": "B19", "lat": 31.84978, "lon": 54.38629, "hwy_id": "135C", "hwy_dir": "C", "km": 37.83, "corridor": "ring", "cat": "MAJ", "first_year": 1966, "replacement_cost": 2796556.0, "spans": 5, "length_m": 186.9, "traffic": 11230, "bci_now": 55.0, "cond_cat_now": "Fair", "priority_rank_now": 134}, "B20": {"id": "B20", "lat": 32.6937, "lon": 54.03303, "hwy_id": "237D", "hwy_dir": "C", "km": 17.35, "corridor": "north", "cat": "STD", "first_year": 1993, "replacement_cost": 132489.0, "spans": 1, "length_m": 8.8, "traffic": 7557, "bci_now": 29.4, "cond_cat_now": "Poor", "priority_rank_now": 39}, "B21": {"id": "B21", "lat": 31.02622, "lon": 54.04479, "hwy_id": "150C", "hwy_dir": "C", "km": 12.08, "corridor": "south", "cat": "MAJ", "first_year": 1979, "replacement_cost": 832058.0, "spans": 3, "length_m": 65.5, "traffic": 1104, "bci_now": 38.4, "cond_cat_now": "Poor", "priority_rank_now": 127}, "B22": {"id": "B22", "lat": 31.8994, "lon": 54.36151, "hwy_id": "6A", "hwy_dir": "C", "km": 3.59, "corridor": "northwest", "cat": "STD", "first_year": 1994, "replacement_cost": 842901.0, "spans": 3, "length_m": 48.6, "traffic": 1098, "bci_now": 32.8, "cond_cat_now": "Poor", "priority_rank_now": 104}, "B23": {"id": "B23", "lat": 31.85305, "lon": 54.39176, "hwy_id": "135C", "hwy_dir": "C", "km": 12.4, "corridor": "ring", "cat": "STD", "first_year": 1974, "replacement_cost": 435773.0, "spans": 3, "length_m": 27.8, "traffic": 7095, "bci_now": 54.7, "cond_cat_now": "Fair", "priority_rank_now": 159}, "B24": {"id": "B24", "lat": 31.237, "lon": 54.21431, "hwy_id": "150A", "hwy_dir": "C", "km": 1.98, "corridor": "south", "cat": "MAJ", "first_year": 1970, "replacement_cost": 2859858.0, "spans": 4, "length_m": 214.1, "traffic": 16521, "bci_now": 39.6, "cond_cat_now": "Poor", "priority_rank_now": 19}, "B25": {"id": "B25", "lat": 32.43694, "lon": 53.99181, "hwy_id": "138C", "hwy_dir": "C", "km": 11.71, "corridor": "north", "cat": "MAJ", "first_year": 1998, "replacement_cost": 1678195.0, "spans": 3, "length_m": 56.7, "traffic": 8037, "bci_now": 43.3, "cond_cat_now": "Poor", "priority_rank_now": 111}, "B26": {"id": "B26", "lat": 31.84089, "lon": 54.36822, "hwy_id": "135E", "hwy_dir": "C", "km": 1.52, "corridor": "ring", "cat": "MAJ", "first_year": 1974, "replacement_cost": 761346.0, "spans": 3, "length_m": 59.4, "traffic": 16827, "bci_now": 41.5, "cond_cat_now": "Poor", "priority_rank_now": 40}, "B27": {"id": "B27", "lat": 32.13902, "lon": 54.12667, "hwy_id": "93A", "hwy_dir": "C", "km": 16.01, "corridor": "north", "cat": "MAJ", "first_year": 1969, "replacement_cost": 2387219.0, "spans": 3, "length_m": 133.7, "traffic": 3755, "bci_now": 48.3, "cond_cat_now": "Poor", "priority_rank_now": 146}, "B28": {"id": "B28", "lat": 31.92513, "lon": 54.32628, "hwy_id": "231B", "hwy_dir": "C", "km": 12.9, "corridor": "ring", "cat": "MAJ", "first_year": 1969, "replacement_cost": 1339917.0, "spans": 3, "length_m": 119.6, "traffic": 3034, "bci_now": 38.5, "cond_cat_now": "Poor", "priority_rank_now": 117}, "B29": {"id": "B29", "lat": 31.84452, "lon": 54.37753, "hwy_id": "135D", "hwy_dir": "C", "km": 18.64, "corridor": "ring", "cat": "MAJ", "first_year": 1967, "replacement_cost": 1138864.0, "spans": 3, "length_m": 85.2, "traffic": 4489, "bci_now": 39.6, "cond_cat_now": "Poor", "priority_rank_now": 114}, "B30": {"id": "B30", "lat": 30.80452, "lon": 55.37552, "hwy_id": "132B", "hwy_dir": "C", "km": 12.22, "corridor": "east", "cat": "MAJ", "first_year": 1956, "replacement_cost": 1438080.0, "spans": 3, "length_m": 84.8, "traffic": 19134, "bci_now": 41.6, "cond_cat_now": "Poor", "priority_rank_now": 23}, "B31": {"id": "B31", "lat": 32.20255, "lon": 53.83925, "hwy_id": "96C", "hwy_dir": "C", "km": 1.54, "corridor": "northwest", "cat": "MAJ", "first_year": 1968, "replacement_cost": 3913923.0, "spans": 5, "length_m": 203.3, "traffic": 10188, "bci_now": 38.8, "cond_cat_now": "Poor", "priority_rank_now": 38}, "B32": {"id": "B32", "lat": 31.8911, "lon": 54.42799, "hwy_id": "78C", "hwy_dir": "R", "km": 23.52, "corridor": "ring", "cat": "STD", "first_year": 1968, "replacement_cost": 1285477.0, "spans": 6, "length_m": 48.8, "traffic": 13004, "bci_now": 53.2, "cond_cat_now": "Fair", "priority_rank_now": 129}, "B33": {"id": "B33", "lat": 31.89215, "lon": 54.42066, "hwy_id": "78C", "hwy_dir": "L", "km": 23.52, "corridor": "ring", "cat": "MAJ", "first_year": 1997, "replacement_cost": 1077560.0, "spans": 3, "length_m": 47.2, "traffic": 17851, "bci_now": 36.8, "cond_cat_now": "Poor", "priority_rank_now": 15}, "B34": {"id": "B34", "lat": 31.75554, "lon": 54.82913, "hwy_id": "72D", "hwy_dir": "R", "km": 52.79, "corridor": "southeast", "cat": "MAJ", "first_year": 1991, "replacement_cost": 1532277.0, "spans": 1, "length_m": 83.5, "traffic": 17795, "bci_now": 33.9, "cond_cat_now": "Poor", "priority_rank_now": 5}, "B35": {"id": "B35", "lat": 31.74953, "lon": 54.82686, "hwy_id": "72D", "hwy_dir": "L", "km": 52.77, "corridor": "southeast", "cat": "MAJ", "first_year": 1959, "replacement_cost": 1011428.0, "spans": 3, "length_m": 52.6, "traffic": 3395, "bci_now": 48.7, "cond_cat_now": "Poor", "priority_rank_now": 152}, "B36": {"id": "B36", "lat": 31.85786, "lon": 54.33429, "hwy_id": "135H", "hwy_dir": "C", "km": 31.23, "corridor": "ring", "cat": "STD", "first_year": 1981, "replacement_cost": 949435.0, "spans": 3, "length_m": 38.6, "traffic": 19933, "bci_now": 47.0, "cond_cat_now": "Poor", "priority_rank_now": 52}, "B37": {"id": "B37", "lat": 31.50223, "lon": 54.38501, "hwy_id": "102A", "hwy_dir": "C", "km": 27.82, "corridor": "south", "cat": "MAJ", "first_year": 1992, "replacement_cost": 743164.0, "spans": 3, "length_m": 31.3, "traffic": 7791, "bci_now": 51.2, "cond_cat_now": "Fair", "priority_rank_now": 148}, "B38": {"id": "B38", "lat": 31.24596, "lon": 55.96957, "hwy_id": "177C", "hwy_dir": "C", "km": 32.35, "corridor": "southeast", "cat": "MAJ", "first_year": 1965, "replacement_cost": 3210660.0, "spans": 5, "length_m": 244.0, "traffic": 8832, "bci_now": 35.3, "cond_cat_now": "Poor", "priority_rank_now": 35}, "B39": {"id": "B39", "lat": 31.86798, "lon": 54.31404, "hwy_id": "231A", "hwy_dir": "C", "km": 0.13, "corridor": "ring", "cat": "MAJ", "first_year": 1973, "replacement_cost": 1848889.0, "spans": 3, "length_m": 134.0, "traffic": 3032, "bci_now": 37.2, "cond_cat_now": "Poor", "priority_rank_now": 107}, "B40": {"id": "B40", "lat": 32.69618, "lon": 53.28533, "hwy_id": "285A", "hwy_dir": "C", "km": 21.93, "corridor": "northwest", "cat": "MAJ", "first_year": 1995, "replacement_cost": 1408566.0, "spans": 3, "length_m": 61.9, "traffic": 6306, "bci_now": 38.6, "cond_cat_now": "Poor", "priority_rank_now": 100}, "B41": {"id": "B41", "lat": 32.46921, "lon": 53.54649, "hwy_id": "141B", "hwy_dir": "C", "km": 0.12, "corridor": "northwest", "cat": "MAJ", "first_year": 1976, "replacement_cost": 3494368.0, "spans": 5, "length_m": 226.2, "traffic": 18291, "bci_now": 49.4, "cond_cat_now": "Poor", "priority_rank_now": 51}, "B42": {"id": "B42", "lat": 31.94189, "lon": 54.37747, "hwy_id": "78A", "hwy_dir": "C", "km": 11.85, "corridor": "ring", "cat": "MAJ", "first_year": 1960, "replacement_cost": 1092484.0, "spans": 3, "length_m": 69.0, "traffic": 19556, "bci_now": 37.7, "cond_cat_now": "Poor", "priority_rank_now": 11}, "B43": {"id": "B43", "lat": 30.43108, "lon": 55.95457, "hwy_id": "195A", "hwy_dir": "C", "km": 1.19, "corridor": "east", "cat": "STD", "first_year": 1990, "replacement_cost": 301816.0, "spans": 2, "length_m": 21.1, "traffic": 14659, "bci_now": 39.5, "cond_cat_now": "Poor", "priority_rank_now": 50}, "B44": {"id": "B44", "lat": 32.28031, "lon": 53.75526, "hwy_id": "96D", "hwy_dir": "C", "km": 10.66, "corridor": "northwest", "cat": "STD", "first_year": 1985, "replacement_cost": 434100.0, "spans": 1, "length_m": 19.2, "traffic": 16714, "bci_now": 44.9, "cond_cat_now": "Poor", "priority_rank_now": 70}, "B45": {"id": "B45", "lat": 31.58479, "lon": 53.98919, "hwy_id": "99A", "hwy_dir": "C", "km": 6.88, "corridor": "southwest", "cat": "MAJ", "first_year": 1956, "replacement_cost": 1022061.0, "spans": 3, "length_m": 80.9, "traffic": 9556, "bci_now": 38.2, "cond_cat_now": "Poor", "priority_rank_now": 75}, "B46": {"id": "B46", "lat": 32.3767, "lon": 53.65009, "hwy_id": "141A", "hwy_dir": "C", "km": 18.36, "corridor": "northwest", "cat": "MAJ", "first_year": 1997, "replacement_cost": 664996.0, "spans": 3, "length_m": 45.4, "traffic": 8261, "bci_now": 51.8, "cond_cat_now": "Fair", "priority_rank_now": 149}, "B47": {"id": "B47", "lat": 30.98084, "lon": 55.21247, "hwy_id": "132A", "hwy_dir": "C", "km": 31.49, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 1112764.0, "spans": 3, "length_m": 47.1, "traffic": 16717, "bci_now": 54.9, "cond_cat_now": "Fair", "priority_rank_now": 121}, "B48": {"id": "B48", "lat": 31.73402, "lon": 54.60015, "hwy_id": "75B", "hwy_dir": "R", "km": 46.79, "corridor": "east", "cat": "MAJ", "first_year": 1958, "replacement_cost": 973664.0, "spans": 3, "length_m": 51.7, "traffic": 2936, "bci_now": 29.3, "cond_cat_now": "Poor", "priority_rank_now": 63}, "B49": {"id": "B49", "lat": 31.72932, "lon": 54.59521, "hwy_id": "75B", "hwy_dir": "L", "km": 46.71, "corridor": "east", "cat": "MAJ", "first_year": 1961, "replacement_cost": 954436.0, "spans": 3, "length_m": 41.4, "traffic": 4815, "bci_now": 52.9, "cond_cat_now": "Fair", "priority_rank_now": 158}, "B50": {"id": "B50", "lat": 31.00731, "lon": 54.02871, "hwy_id": "150C", "hwy_dir": "C", "km": 23.98, "corridor": "south", "cat": "MAJ", "first_year": 1966, "replacement_cost": 4268943.0, "spans": 4, "length_m": 305.9, "traffic": 15596, "bci_now": 51.2, "cond_cat_now": "Fair", "priority_rank_now": 79}, "B51": {"id": "B51", "lat": 32.60962, "lon": 54.00792, "hwy_id": "237A", "hwy_dir": "C", "km": 35.9, "corridor": "north", "cat": "STD", "first_year": 1977, "replacement_cost": 149551.0, "spans": 1, "length_m": 8.8, "traffic": 4567, "bci_now": 48.2, "cond_cat_now": "Poor", "priority_rank_now": 151}, "B52": {"id": "B52", "lat": 31.84271, "lon": 54.37452, "hwy_id": "135D", "hwy_dir": "C", "km": 32.6, "corridor": "ring", "cat": "MAJ", "first_year": 1955, "replacement_cost": 1092159.0, "spans": 3, "length_m": 85.7, "traffic": 1923, "bci_now": 39.2, "cond_cat_now": "Poor", "priority_rank_now": 126}, "B53": {"id": "B53", "lat": 31.41077, "lon": 55.68456, "hwy_id": "177A", "hwy_dir": "C", "km": 53.98, "corridor": "southeast", "cat": "MAJ", "first_year": 1960, "replacement_cost": 8418120.0, "spans": 8, "length_m": 478.5, "traffic": 5843, "bci_now": 42.9, "cond_cat_now": "Poor", "priority_rank_now": 48}, "B54": {"id": "B54", "lat": 31.84465, "lon": 54.3607, "hwy_id": "135E", "hwy_dir": "C", "km": 34.7, "corridor": "ring", "cat": "MAJ", "first_year": 1993, "replacement_cost": 3620732.0, "spans": 2, "length_m": 154.0, "traffic": 6386, "bci_now": 51.4, "cond_cat_now": "Fair", "priority_rank_now": 139}, "B55": {"id": "B55", "lat": 31.86314, "lon": 54.32373, "hwy_id": "135I", "hwy_dir": "C", "km": 17.8, "corridor": "ring", "cat": "MAJ", "first_year": 1929, "replacement_cost": 2383110.0, "spans": 4, "length_m": 203.7, "traffic": 11731, "bci_now": 41.0, "cond_cat_now": "Poor", "priority_rank_now": 59}, "B56": {"id": "B56", "lat": 31.06063, "lon": 55.15942, "hwy_id": "132A", "hwy_dir": "C", "km": 15.11, "corridor": "east", "cat": "MAJ", "first_year": 1972, "replacement_cost": 2405951.0, "spans": 5, "length_m": 109.0, "traffic": 13958, "bci_now": 47.7, "cond_cat_now": "Poor", "priority_rank_now": 87}, "B57": {"id": "B57", "lat": 31.85638, "lon": 54.39729, "hwy_id": "135B", "hwy_dir": "C", "km": 46.63, "corridor": "ring", "cat": "MAJ", "first_year": 1979, "replacement_cost": 1054914.0, "spans": 3, "length_m": 80.5, "traffic": 9588, "bci_now": 42.0, "cond_cat_now": "Poor", "priority_rank_now": 101}, "B58": {"id": "B58", "lat": 32.31571, "lon": 53.71704, "hwy_id": "96D", "hwy_dir": "C", "km": 42.13, "corridor": "northwest", "cat": "STD", "first_year": 1977, "replacement_cost": 662394.0, "spans": 3, "length_m": 36.8, "traffic": 3116, "bci_now": 50.9, "cond_cat_now": "Fair", "priority_rank_now": 161}, "B59": {"id": "B59", "lat": 31.55444, "lon": 53.93675, "hwy_id": "99A", "hwy_dir": "C", "km": 14.92, "corridor": "southwest", "cat": "MAJ", "first_year": 1996, "replacement_cost": 1185958.0, "spans": 3, "length_m": 46.1, "traffic": 15435, "bci_now": 34.5, "cond_cat_now": "Poor", "priority_rank_now": 16}, "B60": {"id": "B60", "lat": 31.88225, "lon": 54.39429, "hwy_id": "75A", "hwy_dir": "R", "km": 11.31, "corridor": "east", "cat": "MAJ", "first_year": 1997, "replacement_cost": 2534100.0, "spans": 3, "length_m": 122.7, "traffic": 3691, "bci_now": 28.3, "cond_cat_now": "Poor", "priority_rank_now": 36}, "B61": {"id": "B61", "lat": 31.87698, "lon": 54.39013, "hwy_id": "75A", "hwy_dir": "L", "km": 11.61, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 3022218.0, "spans": 3, "length_m": 164.2, "traffic": 8995, "bci_now": 46.6, "cond_cat_now": "Poor", "priority_rank_now": 110}, "B62": {"id": "B62", "lat": 31.88163, "lon": 54.39515, "hwy_id": "75A", "hwy_dir": "R", "km": 11.71, "corridor": "east", "cat": "MAJ", "first_year": 1991, "replacement_cost": 1072329.0, "spans": 2, "length_m": 64.9, "traffic": 2359, "bci_now": 39.4, "cond_cat_now": "Poor", "priority_rank_now": 125}, "B63": {"id": "B63", "lat": 31.87629, "lon": 54.39108, "hwy_id": "75A", "hwy_dir": "L", "km": 12.05, "corridor": "east", "cat": "MAJ", "first_year": 1958, "replacement_cost": 914614.0, "spans": 2, "length_m": 44.0, "traffic": 12890, "bci_now": 36.5, "cond_cat_now": "Poor", "priority_rank_now": 37}, "B64": {"id": "B64", "lat": 31.76447, "lon": 54.55787, "hwy_id": "75B", "hwy_dir": "R", "km": 27.17, "corridor": "east", "cat": "MAJ", "first_year": 1958, "replacement_cost": 401053.0, "spans": 1, "length_m": 28.2, "traffic": 10563, "bci_now": 46.9, "cond_cat_now": "Poor", "priority_rank_now": 123}, "B65": {"id": "B65", "lat": 31.75978, "lon": 54.5529, "hwy_id": "75B", "hwy_dir": "L", "km": 27.09, "corridor": "east", "cat": "MAJ", "first_year": 1961, "replacement_cost": 939677.0, "spans": 1, "length_m": 49.1, "traffic": 4399, "bci_now": 51.0, "cond_cat_now": "Fair", "priority_rank_now": 156}, "B66": {"id": "B66", "lat": 32.03603, "lon": 54.04841, "hwy_id": "6G", "hwy_dir": "C", "km": 21.39, "corridor": "northwest", "cat": "MAJ", "first_year": 1999, "replacement_cost": 596781.0, "spans": 1, "length_m": 27.6, "traffic": 9857, "bci_now": 45.6, "cond_cat_now": "Poor", "priority_rank_now": 119}, "B67": {"id": "B67", "lat": 32.02632, "lon": 54.06336, "hwy_id": "6G", "hwy_dir": "C", "km": 10.91, "corridor": "northwest", "cat": "STD", "first_year": 1980, "replacement_cost": 142348.0, "spans": 1, "length_m": 15.8, "traffic": 12626, "bci_now": 30.8, "cond_cat_now": "Poor", "priority_rank_now": 20}, "B68": {"id": "B68", "lat": 31.53329, "lon": 54.40153, "hwy_id": "102A", "hwy_dir": "C", "km": 10.49, "corridor": "south", "cat": "MAJ", "first_year": 1979, "replacement_cost": 2123311.0, "spans": 3, "length_m": 88.9, "traffic": 7507, "bci_now": 38.7, "cond_cat_now": "Poor", "priority_rank_now": 82}, "B69": {"id": "B69", "lat": 32.01998, "lon": 54.07311, "hwy_id": "6G", "hwy_dir": "C", "km": 4.07, "corridor": "northwest", "cat": "STD", "first_year": 1938, "replacement_cost": 50275.0, "spans": 1, "length_m": 5.6, "traffic": 11882, "bci_now": 40.7, "cond_cat_now": "Poor", "priority_rank_now": 85}, "B70": {"id": "B70", "lat": 32.01748, "lon": 54.07696, "hwy_id": "6G", "hwy_dir": "C", "km": 1.38, "corridor": "northwest", "cat": "STD", "first_year": 1940, "replacement_cost": 61579.0, "spans": 1, "length_m": 4.8, "traffic": 4425, "bci_now": 47.5, "cond_cat_now": "Poor", "priority_rank_now": 150}, "B71": {"id": "B71", "lat": 31.79582, "lon": 54.65327, "hwy_id": "72C", "hwy_dir": "L", "km": 26.54, "corridor": "southeast", "cat": "STD", "first_year": 1979, "replacement_cost": 386056.0, "spans": 1, "length_m": 16.8, "traffic": 10823, "bci_now": 32.2, "cond_cat_now": "Poor", "priority_rank_now": 34}, "B72": {"id": "B72", "lat": 31.52893, "lon": 53.8927, "hwy_id": "99A", "hwy_dir": "C", "km": 21.67, "corridor": "southwest", "cat": "MAJ", "first_year": 1980, "replacement_cost": 4655102.0, "spans": 3, "length_m": 309.4, "traffic": 13802, "bci_now": 41.5, "cond_cat_now": "Poor", "priority_rank_now": 26}, "B73": {"id": "B73", "lat": 31.57182, "lon": 53.96678, "hwy_id": "99A", "hwy_dir": "C", "km": 10.32, "corridor": "southwest", "cat": "MAJ", "first_year": 1974, "replacement_cost": 4800542.0, "spans": 5, "length_m": 290.1, "traffic": 16226, "bci_now": 30.7, "cond_cat_now": "Poor", "priority_rank_now": 1}, "B74": {"id": "B74", "lat": 31.85182, "lon": 54.3897, "hwy_id": "135C", "hwy_dir": "C", "km": 21.96, "corridor": "ring", "cat": "MAJ", "first_year": 1983, "replacement_cost": 733077.0, "spans": 1, "length_m": 50.8, "traffic": 16738, "bci_now": 39.5, "cond_cat_now": "Poor", "priority_rank_now": 33}, "B75": {"id": "B75", "lat": 32.28921, "lon": 54.01762, "hwy_id": "138B", "hwy_dir": "C", "km": 0.0, "corridor": "north", "cat": "MAJ", "first_year": 1989, "replacement_cost": 1036414.0, "spans": 1, "length_m": 46.4, "traffic": 8760, "bci_now": 30.4, "cond_cat_now": "Poor", "priority_rank_now": 31}, "B76": {"id": "B76", "lat": 32.11059, "lon": 53.93856, "hwy_id": "96A", "hwy_dir": "C", "km": 39.8, "corridor": "northwest", "cat": "MAJ", "first_year": 1953, "replacement_cost": 635564.0, "spans": 3, "length_m": 54.8, "traffic": 7582, "bci_now": 33.2, "cond_cat_now": "Poor", "priority_rank_now": 58}, "B77": {"id": "B77", "lat": 31.73028, "lon": 54.92383, "hwy_id": "72E", "hwy_dir": "R", "km": 39.83, "corridor": "southeast", "cat": "STD", "first_year": 1981, "replacement_cost": 1140158.0, "spans": 4, "length_m": 56.4, "traffic": 9422, "bci_now": 20.2, "cond_cat_now": "Poor", "priority_rank_now": 2}, "B78": {"id": "B78", "lat": 31.85348, "lon": 54.39247, "hwy_id": "135C", "hwy_dir": "C", "km": 9.08, "corridor": "ring", "cat": "STD", "first_year": 1971, "replacement_cost": 708764.0, "spans": 3, "length_m": 29.8, "traffic": 13052, "bci_now": 35.0, "cond_cat_now": "Poor", "priority_rank_now": 32}, "B79": {"id": "B79", "lat": 31.8882, "lon": 54.42741, "hwy_id": "78C", "hwy_dir": "R", "km": 28.45, "corridor": "ring", "cat": "MAJ", "first_year": 1993, "replacement_cost": 1733380.0, "spans": 3, "length_m": 70.1, "traffic": 6852, "bci_now": 41.8, "cond_cat_now": "Poor", "priority_rank_now": 109}, "B80": {"id": "B80", "lat": 31.88927, "lon": 54.42009, "hwy_id": "78C", "hwy_dir": "L", "km": 28.43, "corridor": "ring", "cat": "MAJ", "first_year": 1994, "replacement_cost": 1723876.0, "spans": 3, "length_m": 70.7, "traffic": 14342, "bci_now": 42.7, "cond_cat_now": "Poor", "priority_rank_now": 55}, "B81": {"id": "B81", "lat": 31.68692, "lon": 54.66556, "hwy_id": "75C", "hwy_dir": "R", "km": 17.12, "corridor": "east", "cat": "MAJ", "first_year": 1983, "replacement_cost": 2343783.0, "spans": 4, "length_m": 142.1, "traffic": 17235, "bci_now": 35.9, "cond_cat_now": "Poor", "priority_rank_now": 7}, "B82": {"id": "B82", "lat": 31.6964, "lon": 54.64093, "hwy_id": "75C", "hwy_dir": "L", "km": 7.92, "corridor": "east", "cat": "MAJ", "first_year": 1994, "replacement_cost": 4152548.0, "spans": 4, "length_m": 222.1, "traffic": 18798, "bci_now": 49.9, "cond_cat_now": "Poor", "priority_rank_now": 44}, "B83": {"id": "B83", "lat": 31.22238, "lon": 54.2035, "hwy_id": "150A", "hwy_dir": "C", "km": 10.77, "corridor": "south", "cat": "MAJ", "first_year": 1988, "replacement_cost": 1179632.0, "spans": 2, "length_m": 59.9, "traffic": 4959, "bci_now": 45.8, "cond_cat_now": "Poor", "priority_rank_now": 142}, "B84": {"id": "B84", "lat": 30.50298, "lon": 55.82493, "hwy_id": "132D", "hwy_dir": "C", "km": 39.88, "corridor": "east", "cat": "MAJ", "first_year": 1965, "replacement_cost": 310407.0, "spans": 3, "length_m": 43.4, "traffic": 3001, "bci_now": 31.9, "cond_cat_now": "Poor", "priority_rank_now": 91}, "B85": {"id": "B85", "lat": 31.71427, "lon": 54.97254, "hwy_id": "105A", "hwy_dir": "C", "km": 60.91, "corridor": "southeast", "cat": "MAJ", "first_year": 1962, "replacement_cost": 2410608.0, "spans": 3, "length_m": 82.9, "traffic": 2299, "bci_now": 32.1, "cond_cat_now": "Poor", "priority_rank_now": 72}, "B86": {"id": "B86", "lat": 31.69513, "lon": 54.65417, "hwy_id": "75C", "hwy_dir": "R", "km": 11.84, "corridor": "east", "cat": "MAJ", "first_year": 2003, "replacement_cost": 2379422.0, "spans": 3, "length_m": 122.9, "traffic": 15744, "bci_now": 48.3, "cond_cat_now": "Poor", "priority_rank_now": 81}, "B87": {"id": "B87", "lat": 31.70464, "lon": 54.62948, "hwy_id": "75C", "hwy_dir": "L", "km": 2.61, "corridor": "east", "cat": "MAJ", "first_year": 1965, "replacement_cost": 3458490.0, "spans": 4, "length_m": 126.0, "traffic": 10781, "bci_now": 44.2, "cond_cat_now": "Poor", "priority_rank_now": 77}, "B88": {"id": "B88", "lat": 32.15043, "lon": 53.89554, "hwy_id": "96B", "hwy_dir": "C", "km": 15.2, "corridor": "northwest", "cat": "STD", "first_year": 1949, "replacement_cost": 44744.0, "spans": 1, "length_m": 3.5, "traffic": 2100, "bci_now": 46.1, "cond_cat_now": "Poor", "priority_rank_now": 154}, "B89": {"id": "B89", "lat": 32.69065, "lon": 54.03208, "hwy_id": "237D", "hwy_dir": "C", "km": 15.84, "corridor": "north", "cat": "STD", "first_year": 1996, "replacement_cost": 135374.0, "spans": 1, "length_m": 9.6, "traffic": 17630, "bci_now": 43.7, "cond_cat_now": "Poor", "priority_rank_now": 54}, "B90": {"id": "B90", "lat": 31.47447, "lon": 55.59326, "hwy_id": "177A", "hwy_dir": "C", "km": 20.34, "corridor": "southeast", "cat": "MAJ", "first_year": 1958, "replacement_cost": 2775439.0, "spans": 8, "length_m": 261.4, "traffic": 18119, "bci_now": 49.8, "cond_cat_now": "Poor", "priority_rank_now": 66}, "B91": {"id": "B91", "lat": 31.44059, "lon": 55.64181, "hwy_id": "177A", "hwy_dir": "C", "km": 38.23, "corridor": "southeast", "cat": "STD", "first_year": 1982, "replacement_cost": 719380.0, "spans": 3, "length_m": 47.2, "traffic": 8054, "bci_now": 31.8, "cond_cat_now": "Poor", "priority_rank_now": 45}, "B92": {"id": "B92", "lat": 32.11427, "lon": 53.93459, "hwy_id": "96A", "hwy_dir": "C", "km": 43.06, "corridor": "northwest", "cat": "STD", "first_year": 1948, "replacement_cost": 49228.0, "spans": 1, "length_m": 2.6, "traffic": 6893, "bci_now": 32.0, "cond_cat_now": "Poor", "priority_rank_now": 62}, "B93": {"id": "B93", "lat": 31.33521, "lon": 55.81339, "hwy_id": "177B", "hwy_dir": "C", "km": 38.65, "corridor": "southeast", "cat": "MAJ", "first_year": 1966, "replacement_cost": 2600623.0, "spans": 3, "length_m": 112.0, "traffic": 15603, "bci_now": 56.0, "cond_cat_now": "Fair", "priority_rank_now": 120}, "B94": {"id": "B94", "lat": 31.75753, "lon": 54.5675, "hwy_id": "75B", "hwy_dir": "R", "km": 31.64, "corridor": "east", "cat": "MAJ", "first_year": 1961, "replacement_cost": 1389661.0, "spans": 3, "length_m": 80.6, "traffic": 10662, "bci_now": 40.7, "cond_cat_now": "Poor", "priority_rank_now": 80}, "B95": {"id": "B95", "lat": 31.75278, "lon": 54.56262, "hwy_id": "75B", "hwy_dir": "L", "km": 31.6, "corridor": "east", "cat": "MAJ", "first_year": 1959, "replacement_cost": 1565197.0, "spans": 3, "length_m": 83.6, "traffic": 7353, "bci_now": 48.7, "cond_cat_now": "Poor", "priority_rank_now": 137}, "B96": {"id": "B96", "lat": 32.41537, "lon": 54.00341, "hwy_id": "138C", "hwy_dir": "L", "km": 0.49, "corridor": "north", "cat": "MAJ", "first_year": 1975, "replacement_cost": 5451790.0, "spans": 3, "length_m": 131.6, "traffic": 6821, "bci_now": 42.5, "cond_cat_now": "Poor", "priority_rank_now": 73}, "B97": {"id": "B97", "lat": 31.2608, "lon": 55.94359, "hwy_id": "177C", "hwy_dir": "C", "km": 23.42, "corridor": "southeast", "cat": "MAJ", "first_year": 1959, "replacement_cost": 966845.0, "spans": 3, "length_m": 65.0, "traffic": 8547, "bci_now": 47.5, "cond_cat_now": "Poor", "priority_rank_now": 128}, "B98": {"id": "B98", "lat": 31.20908, "lon": 55.06726, "hwy_id": "75G", "hwy_dir": "R", "km": 25.29, "corridor": "east", "cat": "MAJ", "first_year": 1960, "replacement_cost": 1508536.0, "spans": 3, "length_m": 66.0, "traffic": 12727, "bci_now": 31.5, "cond_cat_now": "Poor", "priority_rank_now": 13}, "B99": {"id": "B99", "lat": 31.2075, "lon": 55.06825, "hwy_id": "75G", "hwy_dir": "R", "km": 26.04, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 1215907.0, "spans": 4, "length_m": 94.9, "traffic": 3902, "bci_now": 52.7, "cond_cat_now": "Fair", "priority_rank_now": 160}, "B100": {"id": "B100", "lat": 31.20478, "lon": 55.06158, "hwy_id": "75G", "hwy_dir": "L", "km": 25.91, "corridor": "east", "cat": "MAJ", "first_year": 1970, "replacement_cost": 2599226.0, "spans": 4, "length_m": 104.7, "traffic": 10054, "bci_now": 52.2, "cond_cat_now": "Fair", "priority_rank_now": 130}, "B101": {"id": "B101", "lat": 31.20002, "lon": 55.06456, "hwy_id": "75G", "hwy_dir": "L", "km": 28.16, "corridor": "east", "cat": "MAJ", "first_year": 1987, "replacement_cost": 2021881.0, "spans": 2, "length_m": 96.2, "traffic": 1597, "bci_now": 33.2, "cond_cat_now": "Poor", "priority_rank_now": 90}, "B102": {"id": "B102", "lat": 31.19726, "lon": 55.07464, "hwy_id": "75G", "hwy_dir": "R", "km": 30.86, "corridor": "east", "cat": "MAJ", "first_year": 1967, "replacement_cost": 5723179.0, "spans": 4, "length_m": 247.3, "traffic": 4396, "bci_now": 33.4, "cond_cat_now": "Poor", "priority_rank_now": 30}, "B103": {"id": "B103", "lat": 31.19447, "lon": 55.06803, "hwy_id": "75G", "hwy_dir": "L", "km": 30.78, "corridor": "east", "cat": "MAJ", "first_year": 1964, "replacement_cost": 4596581.0, "spans": 4, "length_m": 345.3, "traffic": 14344, "bci_now": 50.8, "cond_cat_now": "Fair", "priority_rank_now": 83}, "B104": {"id": "B104", "lat": 31.18262, "lon": 55.07544, "hwy_id": "75G", "hwy_dir": "L", "km": 36.37, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 2591377.0, "spans": 4, "length_m": 150.4, "traffic": 14898, "bci_now": 42.9, "cond_cat_now": "Poor", "priority_rank_now": 46}, "B105": {"id": "B105", "lat": 30.6855, "lon": 55.53526, "hwy_id": "132B", "hwy_dir": "C", "km": 44.63, "corridor": "east", "cat": "MAJ", "first_year": 1963, "replacement_cost": 1668359.0, "spans": 3, "length_m": 85.9, "traffic": 16025, "bci_now": 38.0, "cond_cat_now": "Poor", "priority_rank_now": 22}, "B106": {"id": "B106", "lat": 31.94328, "lon": 54.37413, "hwy_id": "78A", "hwy_dir": "C", "km": 6.56, "corridor": "ring", "cat": "MAJ", "first_year": 1967, "replacement_cost": 1944868.0, "spans": 3, "length_m": 92.8, "traffic": 11028, "bci_now": 39.3, "cond_cat_now": "Poor", "priority_rank_now": 56}, "B107": {"id": "B107", "lat": 31.38013, "lon": 54.32413, "hwy_id": "102B", "hwy_dir": "R", "km": 35.22, "corridor": "south", "cat": "MAJ", "first_year": 1999, "replacement_cost": 2786766.0, "spans": 2, "length_m": 163.1, "traffic": 2216, "bci_now": 43.8, "cond_cat_now": "Poor", "priority_rank_now": 131}, "B108": {"id": "B108", "lat": 31.38275, "lon": 54.31741, "hwy_id": "102B", "hwy_dir": "L", "km": 35.21, "corridor": "south", "cat": "MAJ", "first_year": 1967, "replacement_cost": 2037573.0, "spans": 5, "length_m": 86.6, "traffic": 5478, "bci_now": 27.9, "cond_cat_now": "Poor", "priority_rank_now": 28}, "B109": {"id": "B109", "lat": 31.88199, "lon": 54.38316, "hwy_id": "75A", "hwy_dir": "L", "km": 8.38, "corridor": "east", "cat": "MAJ", "first_year": 1974, "replacement_cost": 2068714.0, "spans": 3, "length_m": 77.3, "traffic": 8837, "bci_now": 46.5, "cond_cat_now": "Poor", "priority_rank_now": 118}, "B110": {"id": "B110", "lat": 31.88896, "lon": 54.38211, "hwy_id": "72A", "hwy_dir": "L", "km": 8.18, "corridor": "southeast", "cat": "MAJ", "first_year": 1973, "replacement_cost": 1005353.0, "spans": 4, "length_m": 95.2, "traffic": 10253, "bci_now": 50.7, "cond_cat_now": "Fair", "priority_rank_now": 133}, "B111": {"id": "B111", "lat": 31.84349, "lon": 54.37033, "hwy_id": "135E", "hwy_dir": "L", "km": 0.52, "corridor": "ring", "cat": "MAJ", "first_year": 1972, "replacement_cost": 2003476.0, "spans": 4, "length_m": 132.5, "traffic": 11175, "bci_now": 46.9, "cond_cat_now": "Poor", "priority_rank_now": 108}, "B112": {"id": "B112", "lat": 31.88676, "lon": 54.38849, "hwy_id": "72A", "hwy_dir": "L", "km": 11.44, "corridor": "southeast", "cat": "MAJ", "first_year": 1972, "replacement_cost": 1020112.0, "spans": 4, "length_m": 88.7, "traffic": 7956, "bci_now": 47.7, "cond_cat_now": "Poor", "priority_rank_now": 132}, "B113": {"id": "B113", "lat": 31.93017, "lon": 54.34524, "hwy_id": "231B", "hwy_dir": "L", "km": 31.44, "corridor": "ring", "cat": "MAJ", "first_year": 1966, "replacement_cost": 1711681.0, "spans": 4, "length_m": 70.0, "traffic": 5284, "bci_now": 36.7, "cond_cat_now": "Poor", "priority_rank_now": 89}, "B114": {"id": "B114", "lat": 31.14274, "lon": 54.13927, "hwy_id": "150B", "hwy_dir": "L", "km": 0.01, "corridor": "south", "cat": "MAJ", "first_year": 1964, "replacement_cost": 2234266.0, "spans": 3, "length_m": 78.6, "traffic": 19596, "bci_now": 38.0, "cond_cat_now": "Poor", "priority_rank_now": 6}, "B115": {"id": "B115", "lat": 31.37741, "lon": 53.64445, "hwy_id": "144A", "hwy_dir": "L", "km": 0.4, "corridor": "southwest", "cat": "MAJ", "first_year": 1965, "replacement_cost": 2791471.0, "spans": 4, "length_m": 132.3, "traffic": 11744, "bci_now": 50.0, "cond_cat_now": "Fair", "priority_rank_now": 112}, "B116": {"id": "B116", "lat": 31.91313, "lon": 54.43239, "hwy_id": "78B", "hwy_dir": "R", "km": 46.02, "corridor": "ring", "cat": "MAJ", "first_year": 1969, "replacement_cost": 2300394.0, "spans": 4, "length_m": 153.9, "traffic": 7612, "bci_now": 55.9, "cond_cat_now": "Fair", "priority_rank_now": 153}, "B117": {"id": "B117", "lat": 31.91438, "lon": 54.42511, "hwy_id": "78B", "hwy_dir": "L", "km": 45.68, "corridor": "ring", "cat": "MAJ", "first_year": 1967, "replacement_cost": 3869660.0, "spans": 4, "length_m": 164.2, "traffic": 1813, "bci_now": 46.8, "cond_cat_now": "Poor", "priority_rank_now": 141}, "B118": {"id": "B118", "lat": 31.93711, "lon": 54.25867, "hwy_id": "6B", "hwy_dir": "L", "km": 5.95, "corridor": "northwest", "cat": "MAJ", "first_year": 1980, "replacement_cost": 3034729.0, "spans": 2, "length_m": 151.8, "traffic": 14165, "bci_now": 51.0, "cond_cat_now": "Fair", "priority_rank_now": 102}, "B119": {"id": "B119", "lat": 31.35292, "lon": 54.96899, "hwy_id": "75F", "hwy_dir": "L", "km": 16.03, "corridor": "east", "cat": "MAJ", "first_year": 1981, "replacement_cost": 1680628.0, "spans": 1, "length_m": 69.9, "traffic": 6899, "bci_now": 48.2, "cond_cat_now": "Poor", "priority_rank_now": 136}, "B120": {"id": "B120", "lat": 31.84877, "lon": 54.35246, "hwy_id": "135F", "hwy_dir": "C", "km": 11.05, "corridor": "ring", "cat": "MAJ", "first_year": 1974, "replacement_cost": 3459684.0, "spans": 4, "length_m": 172.2, "traffic": 16322, "bci_now": 45.6, "cond_cat_now": "Poor", "priority_rank_now": 42}, "B121": {"id": "B121", "lat": 31.60042, "lon": 54.77424, "hwy_id": "75D", "hwy_dir": "L", "km": 9.74, "corridor": "east", "cat": "MAJ", "first_year": 1976, "replacement_cost": 3151764.0, "spans": 2, "length_m": 165.2, "traffic": 15440, "bci_now": 35.5, "cond_cat_now": "Poor", "priority_rank_now": 8}, "B122": {"id": "B122", "lat": 31.60548, "lon": 54.76721, "hwy_id": "75D", "hwy_dir": "L", "km": 6.48, "corridor": "east", "cat": "MAJ", "first_year": 1970, "replacement_cost": 804281.0, "spans": 1, "length_m": 16.7, "traffic": 16159, "bci_now": 47.2, "cond_cat_now": "Poor", "priority_rank_now": 86}, "B123": {"id": "B123", "lat": 31.8595, "lon": 54.48729, "hwy_id": "72B", "hwy_dir": "R", "km": 0.5, "corridor": "southeast", "cat": "MAJ", "first_year": 1980, "replacement_cost": 2623711.0, "spans": 3, "length_m": 97.4, "traffic": 1694, "bci_now": 50.7, "cond_cat_now": "Fair", "priority_rank_now": 155}, "B124": {"id": "B124", "lat": 31.85363, "lon": 54.48458, "hwy_id": "72B", "hwy_dir": "L", "km": 0.54, "corridor": "southeast", "cat": "MAJ", "first_year": 1974, "replacement_cost": 1064375.0, "spans": 3, "length_m": 68.8, "traffic": 18821, "bci_now": 37.2, "cond_cat_now": "Poor", "priority_rank_now": 12}, "B125": {"id": "B125", "lat": 31.85438, "lon": 54.50216, "hwy_id": "72B", "hwy_dir": "R", "km": 8.1, "corridor": "southeast", "cat": "MAJ", "first_year": 1974, "replacement_cost": 1878446.0, "spans": 2, "length_m": 82.4, "traffic": 10940, "bci_now": 33.9, "cond_cat_now": "Poor", "priority_rank_now": 29}, "B126": {"id": "B126", "lat": 31.8485, "lon": 54.49946, "hwy_id": "72B", "hwy_dir": "L", "km": 8.15, "corridor": "southeast", "cat": "MAJ", "first_year": 1970, "replacement_cost": 1742573.0, "spans": 2, "length_m": 93.0, "traffic": 17381, "bci_now": 43.9, "cond_cat_now": "Poor", "priority_rank_now": 43}, "B127": {"id": "B127", "lat": 31.8485, "lon": 54.49946, "hwy_id": "72B", "hwy_dir": "L", "km": 8.15, "corridor": "southeast", "cat": "MAJ", "first_year": 1975, "replacement_cost": 730429.0, "spans": 2, "length_m": 75.9, "traffic": 4176, "bci_now": 35.0, "cond_cat_now": "Poor", "priority_rank_now": 99}, "B128": {"id": "B128", "lat": 31.84346, "lon": 54.51408, "hwy_id": "72B", "hwy_dir": "L", "km": 15.62, "corridor": "southeast", "cat": "MAJ", "first_year": 1976, "replacement_cost": 996318.0, "spans": 4, "length_m": 153.6, "traffic": 1271, "bci_now": 31.8, "cond_cat_now": "Poor", "priority_rank_now": 97}, "B129": {"id": "B129", "lat": 31.46948, "lon": 54.89613, "hwy_id": "75E", "hwy_dir": "L", "km": 21.05, "corridor": "east", "cat": "MAJ", "first_year": 1975, "replacement_cost": 2090032.0, "spans": 2, "length_m": 121.1, "traffic": 14494, "bci_now": 37.6, "cond_cat_now": "Poor", "priority_rank_now": 24}, "B130": {"id": "B130", "lat": 31.54512, "lon": 54.40782, "hwy_id": "102A", "hwy_dir": "C", "km": 3.88, "corridor": "south", "cat": "MAJ", "first_year": 1979, "replacement_cost": 4314114.0, "spans": 5, "length_m": 325.0, "traffic": 11872, "bci_now": 43.0, "cond_cat_now": "Poor", "priority_rank_now": 49}, "B131": {"id": "B131", "lat": 31.70044, "lon": 54.64679, "hwy_id": "75C", "hwy_dir": "R", "km": 8.42, "corridor": "east", "cat": "MAJ", "first_year": 2001, "replacement_cost": 1151393.0, "spans": 1, "length_m": 47.2, "traffic": 19446, "bci_now": 51.8, "cond_cat_now": "Fair", "priority_rank_now": 88}, "B132": {"id": "B132", "lat": 31.7003, "lon": 54.64699, "hwy_id": "75C", "hwy_dir": "R", "km": 8.51, "corridor": "east", "cat": "MAJ", "first_year": 2008, "replacement_cost": 1537443.0, "spans": 1, "length_m": 66.2, "traffic": 1968, "bci_now": 44.1, "cond_cat_now": "Poor", "priority_rank_now": 145}, "B133": {"id": "B133", "lat": 30.4035, "lon": 56.00084, "hwy_id": "195A", "hwy_dir": "L", "km": 4.01, "corridor": "east", "cat": "MAJ", "first_year": 1985, "replacement_cost": 2564328.0, "spans": 4, "length_m": 121.3, "traffic": 7574, "bci_now": 37.9, "cond_cat_now": "Poor", "priority_rank_now": 69}, "B134": {"id": "B134", "lat": 31.49352, "lon": 54.88111, "hwy_id": "75E", "hwy_dir": "L", "km": 9.71, "corridor": "east", "cat": "MAJ", "first_year": 1979, "replacement_cost": 2295859.0, "spans": 2, "length_m": 145.7, "traffic": 9564, "bci_now": 39.4, "cond_cat_now": "Poor", "priority_rank_now": 67}, "B135": {"id": "B135", "lat": 31.84896, "lon": 54.35207, "hwy_id": "135F", "hwy_dir": "C", "km": 12.77, "corridor": "ring", "cat": "MAJ", "first_year": 1972, "replacement_cost": 2249806.0, "spans": 3, "length_m": 88.7, "traffic": 7258, "bci_now": 35.8, "cond_cat_now": "Poor", "priority_rank_now": 61}, "B136": {"id": "B136", "lat": 31.83792, "lon": 54.38062, "hwy_id": "66B", "hwy_dir": "C", "km": 10.25, "corridor": "south", "cat": "MAJ", "first_year": 1987, "replacement_cost": 2084828.0, "spans": 3, "length_m": 91.2, "traffic": 8232, "bci_now": 41.5, "cond_cat_now": "Poor", "priority_rank_now": 95}, "B137": {"id": "B137", "lat": 31.81771, "lon": 54.6085, "hwy_id": "72C", "hwy_dir": "R", "km": 2.44, "corridor": "southeast", "cat": "MAJ", "first_year": 1982, "replacement_cost": 665709.0, "spans": 3, "length_m": 40.9, "traffic": 16122, "bci_now": 43.1, "cond_cat_now": "Poor", "priority_rank_now": 60}, "B138": {"id": "B138", "lat": 31.81187, "lon": 54.6057, "hwy_id": "72C", "hwy_dir": "L", "km": 2.44, "corridor": "southeast", "cat": "MAJ", "first_year": 1976, "replacement_cost": 854143.0, "spans": 3, "length_m": 46.4, "traffic": 14225, "bci_now": 41.1, "cond_cat_now": "Poor", "priority_rank_now": 57}, "B139": {"id": "B139", "lat": 31.56966, "lon": 54.81697, "hwy_id": "75D", "hwy_dir": "L", "km": 29.55, "corridor": "east", "cat": "MAJ", "first_year": 1983, "replacement_cost": 1941204.0, "spans": 2, "length_m": 102.3, "traffic": 18606, "bci_now": 37.4, "cond_cat_now": "Poor", "priority_rank_now": 9}, "B140": {"id": "B140", "lat": 32.6018, "lon": 53.39786, "hwy_id": "285A", "hwy_dir": "C", "km": 0.0, "corridor": "northwest", "cat": "MAJ", "first_year": 1983, "replacement_cost": 2125798.0, "spans": 2, "length_m": 136.0, "traffic": 14537, "bci_now": 43.3, "cond_cat_now": "Poor", "priority_rank_now": 53}, "B141": {"id": "B141", "lat": 31.57774, "lon": 54.80574, "hwy_id": "75D", "hwy_dir": "L", "km": 24.35, "corridor": "east", "cat": "MAJ", "first_year": 1984, "replacement_cost": 1533218.0, "spans": 2, "length_m": 146.5, "traffic": 2852, "bci_now": 44.1, "cond_cat_now": "Poor", "priority_rank_now": 143}, "B142": {"id": "B142", "lat": 31.60336, "lon": 54.77016, "hwy_id": "75D", "hwy_dir": "L", "km": 7.85, "corridor": "east", "cat": "MAJ", "first_year": 1983, "replacement_cost": 684419.0, "spans": 4, "length_m": 203.0, "traffic": 9403, "bci_now": 38.8, "cond_cat_now": "Poor", "priority_rank_now": 84}, "B143": {"id": "B143", "lat": 31.8544, "lon": 54.34119, "hwy_id": "135H", "hwy_dir": "C", "km": 0.76, "corridor": "ring", "cat": "MAJ", "first_year": 1980, "replacement_cost": 1276412.0, "spans": 1, "length_m": 55.5, "traffic": 12783, "bci_now": 38.6, "cond_cat_now": "Poor", "priority_rank_now": 47}, "B144": {"id": "B144", "lat": 31.85103, "lon": 54.38838, "hwy_id": "135C", "hwy_dir": "C", "km": 28.11, "corridor": "ring", "cat": "MAJ", "first_year": 1983, "replacement_cost": 750912.0, "spans": 1, "length_m": 57.1, "traffic": 3497, "bci_now": 43.3, "cond_cat_now": "Poor", "priority_rank_now": 140}, "B145": {"id": "B145", "lat": 31.87338, "lon": 54.33469, "hwy_id": "9A", "hwy_dir": "L", "km": 5.45, "corridor": "southwest", "cat": "MAJ", "first_year": 1983, "replacement_cost": 5979219.0, "spans": 4, "length_m": 192.9, "traffic": 2411, "bci_now": 39.0, "cond_cat_now": "Poor", "priority_rank_now": 78}, "B146": {"id": "B146", "lat": 31.33489, "lon": 54.98026, "hwy_id": "75F", "hwy_dir": "L", "km": 24.54, "corridor": "east", "cat": "MAJ", "first_year": 2012, "replacement_cost": 2235316.0, "spans": 3, "length_m": 156.5, "traffic": 7945, "bci_now": 43.2, "cond_cat_now": "Poor", "priority_rank_now": 105}, "B147": {"id": "B147", "lat": 31.85596, "lon": 54.33807, "hwy_id": "135H", "hwy_dir": "C", "km": 14.53, "corridor": "ring", "cat": "MAJ", "first_year": 1989, "replacement_cost": 1302748.0, "spans": 3, "length_m": 67.5, "traffic": 6605, "bci_now": 24.8, "cond_cat_now": "Poor", "priority_rank_now": 18}, "B148": {"id": "B148", "lat": 31.39946, "lon": 54.33035, "hwy_id": "102B", "hwy_dir": "C", "km": 25.16, "corridor": "south", "cat": "STD", "first_year": 1990, "replacement_cost": 346883.0, "spans": 1, "length_m": 18.1, "traffic": 14208, "bci_now": 31.3, "cond_cat_now": "Poor", "priority_rank_now": 14}, "B149": {"id": "B149", "lat": 31.2125, "lon": 55.05676, "hwy_id": "75G", "hwy_dir": "L", "km": 22.27, "corridor": "east", "cat": "MAJ", "first_year": 2000, "replacement_cost": 4515795.0, "spans": 3, "length_m": 128.5, "traffic": 4166, "bci_now": 37.1, "cond_cat_now": "Poor", "priority_rank_now": 68}, "B150": {"id": "B150", "lat": 31.80265, "lon": 54.65246, "hwy_id": "72C", "hwy_dir": "R", "km": 25.04, "corridor": "southeast", "cat": "STD", "first_year": 1986, "replacement_cost": 273414.0, "spans": 1, "length_m": 14.7, "traffic": 19061, "bci_now": 38.5, "cond_cat_now": "Poor", "priority_rank_now": 21}, "B151": {"id": "B151", "lat": 31.76769, "lon": 54.3961, "hwy_id": "66B", "hwy_dir": "C", "km": 22.35, "corridor": "south", "cat": "MAJ", "first_year": 1988, "replacement_cost": 696802.0, "spans": 3, "length_m": 38.0, "traffic": 6271, "bci_now": 36.4, "cond_cat_now": "Poor", "priority_rank_now": 92}, "B152": {"id": "B152", "lat": 32.42032, "lon": 53.60124, "hwy_id": "141A", "hwy_dir": "C", "km": 38.05, "corridor": "northwest", "cat": "MAJ", "first_year": 1990, "replacement_cost": 1244526.0, "spans": 2, "length_m": 45.0, "traffic": 15398, "bci_now": 49.4, "cond_cat_now": "Poor", "priority_rank_now": 103}, "B153": {"id": "B153", "lat": 30.82075, "lon": 55.35375, "hwy_id": "132B", "hwy_dir": "C", "km": 7.8, "corridor": "east", "cat": "STD", "first_year": 1960, "replacement_cost": 54041.0, "spans": 1, "length_m": 2.8, "traffic": 16411, "bci_now": 44.3, "cond_cat_now": "Poor", "priority_rank_now": 74}, "B154": {"id": "B154", "lat": 31.92463, "lon": 54.42732, "hwy_id": "78B", "hwy_dir": "R", "km": 28.36, "corridor": "ring", "cat": "MAJ", "first_year": 2000, "replacement_cost": 8186037.0, "spans": 3, "length_m": 327.5, "traffic": 19594, "bci_now": 45.7, "cond_cat_now": "Poor", "priority_rank_now": 3}, "B155": {"id": "B155", "lat": 31.91906, "lon": 54.42382, "hwy_id": "78B", "hwy_dir": "L", "km": 28.01, "corridor": "ring", "cat": "MAJ", "first_year": 2003, "replacement_cost": 4924258.0, "spans": 3, "length_m": 240.2, "traffic": 15337, "bci_now": 43.6, "cond_cat_now": "Poor", "priority_rank_now": 25}, "B156": {"id": "B156", "lat": 31.91826, "lon": 54.42575, "hwy_id": "78B", "hwy_dir": "L", "km": 31.07, "corridor": "ring", "cat": "MAJ", "first_year": 1998, "replacement_cost": 3555210.0, "spans": 3, "length_m": 213.6, "traffic": 17837, "bci_now": 50.7, "cond_cat_now": "Fair", "priority_rank_now": 65}, "B157": {"id": "B157", "lat": 31.93207, "lon": 54.40945, "hwy_id": "78B", "hwy_dir": "R", "km": 0.01, "corridor": "ring", "cat": "MAJ", "first_year": 1994, "replacement_cost": 1823820.0, "spans": 2, "length_m": 107.4, "traffic": 14128, "bci_now": 45.1, "cond_cat_now": "Poor", "priority_rank_now": 76}, "B158": {"id": "B158", "lat": 31.93066, "lon": 54.39599, "hwy_id": "78A", "hwy_dir": "L", "km": 43.84, "corridor": "ring", "cat": "MAJ", "first_year": 1994, "replacement_cost": 1288239.0, "spans": 2, "length_m": 85.3, "traffic": 19162, "bci_now": 41.9, "cond_cat_now": "Poor", "priority_rank_now": 27}, "B159": {"id": "B159", "lat": 31.96157, "lon": 54.16511, "hwy_id": "6C", "hwy_dir": "R", "km": 0.31, "corridor": "northwest", "cat": "MAJ", "first_year": 2008, "replacement_cost": 1685968.0, "spans": 1, "length_m": 91.8, "traffic": 11552, "bci_now": 48.0, "cond_cat_now": "Poor", "priority_rank_now": 113}, "B160": {"id": "B160", "lat": 31.92395, "lon": 54.42895, "hwy_id": "78B", "hwy_dir": "R", "km": 30.95, "corridor": "ring", "cat": "MAJ", "first_year": 1994, "replacement_cost": 953884.0, "spans": 1, "length_m": 65.2, "traffic": 15677, "bci_now": 48.1, "cond_cat_now": "Poor", "priority_rank_now": 96}, "B161": {"id": "B161", "lat": 31.91838, "lon": 54.42546, "hwy_id": "78B", "hwy_dir": "L", "km": 30.61, "corridor": "ring", "cat": "MAJ", "first_year": 1998, "replacement_cost": 1244061.0, "spans": 1, "length_m": 49.1, "traffic": 17806, "bci_now": 52.7, "cond_cat_now": "Fair", "priority_rank_now": 106}};
    summary_json = json.dumps(
      summary,
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