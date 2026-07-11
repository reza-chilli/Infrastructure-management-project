# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

from datetime import date

# %%
# calculate current year dynamically to be used further on
current_date = date.today()
current_year = current_date.year
print('Current Year: ', current_year)

# %%

excel_path = "ToR Structures_Data_Updated- bahman 1405.xlsx"
df_raw= pd.read_excel(
  excel_path, 
  skiprows = 2, 
  header=None,
  sheet_name="Bridge Data"
  )
df_trim = df_raw.replace(r"^\s*$", np.nan, regex=True)

# %%
df_trim.columns = [
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

# %%
display(df_trim.columns.tolist())

# %%
display(df_trim.info())

# %%
display(df_trim.describe().T)

# %%
display(df_trim.head(5))

# %%
df_trim["Insp_Year"] = pd.to_numeric(
    df_trim["Insp_Date"].astype(str).str.split("-").str[-1], errors="coerce"
)

df_trim["Years_Passed"] = current_year - df_trim["Insp_Year"]

# %%
cond_cols = ["Cond_Rat_Deck", "Cond_Rat_Super", "Cond_Rat_Sub"]
for col in cond_cols:
    df_trim[col] = pd.to_numeric(df_trim[col], errors="coerce")

# %%
df_trim["Unique_Span_Type"] = (
    df_trim["Unique_Span_Type"].astype(str).str.strip()
)

# %%
bridge_types = {
  "Standard": {
    "Timber": ["TP", "TT"],
    "Prestressed": ["SCC", "SM", "SMC", "VS", "VSO"],
    "Precast": ["HC"],
  },
  "Major": {
    "Concrete": {
      "Pre_stressed_girder": ["CBC", "DBC", "CBT", "DBT", "FC", "FM", "LF", "PJ", "PM", "PO", "PQ", "RD", "RM", "VF"],
      "Pre_cast_girder": ["PE"],
      "Cast_in_place": ["CA", "CF", "CS", "CT", "CV", "CX"],
    },
    "Steel": {
      "Beam": ["FR", "WG", "RB", "RG"],
      "Truss": ["TH"],
    },
  },
}

# %%
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
            if unique_span_type in bridge_types["Major"]["Concrete"]["Pre_stressed_girder"]:
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
            if unique_span_type in bridge_types["Major"]["Concrete"]["Pre_cast_girder"]:
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
            if unique_span_type in bridge_types["Major"]["Concrete"]["Cast_in_place"]:
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
            if unique_span_type in bridge_types["Major"]["Steel"]["Beam"]:
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
            if unique_span_type in bridge_types["Major"]["Steel"]["Truss"]:
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

# %%
df_trim['current_Cond_Rat_Deck'] = df_trim.apply(
    lambda row: calculate_decay(
        int(row['Cond_Rat_Deck']),
        row['Bridge_Cat'],
        row['Unique_Span_Type'],
        int(row['Years_Passed'])
    ), axis=1
)

df_trim['current_Cond_Rat_Super'] = df_trim.apply(
    lambda row: calculate_decay(
        int(row['Cond_Rat_Super']),
        row['Bridge_Cat'],
        row['Unique_Span_Type'],
        int(row['Years_Passed'])
    ), axis=1
)

df_trim['current_Cond_Rat_Sub'] = df_trim.apply(
    lambda row: calculate_decay(
        int(row['Cond_Rat_Sub']),
        row['Bridge_Cat'],
        row['Unique_Span_Type'],
        int(row['Years_Passed'])
    ), axis=1
)

# %%
display(df_trim.head(3))

# %%
bridge_deck_weight = 0.3
bridge_super_structure_weight = 0.35
bridge_sub_structure_weight = 0.35

df_trim["BCI"] = (bridge_deck_weight * df_trim["current_Cond_Rat_Deck"] + 
  bridge_super_structure_weight * df_trim["current_Cond_Rat_Super"] + 
  bridge_sub_structure_weight * df_trim["current_Cond_Rat_Sub"]
  )
display(df_trim.head(3))

# %%
summary = pd.DataFrame({
    "Type": df_trim.dtypes,
    "Missing": df_trim.isna().sum(),
    "Missing %": (df_trim.isna().sum()/len(df_trim)*100).round(2),
    "Unique": df_trim.nunique()
})

display(summary)

# %%
df_trim.describe().T

# %%
df_trim["Age"] = current_year - df_trim["First_Year_In_Service"]

df_trim["Condition"] = (
    df_trim["Cond_Rat_Deck"] +
    df_trim["Cond_Rat_Super"] +
    df_trim["Cond_Rat_Sub"]
) / 3

# %%
print(f"Number of Bridges: {len(df_trim)}")

print(f"Average Age: {df_trim['Age'].mean():.1f}")

print(f"Average Condition: {df_trim['Condition'].mean():.1f}")

print(f"Minimum Condition: {df_trim['Condition'].min():.1f}")

print(f"Maximum Condition: {df_trim['Condition'].max():.1f}")

# %%
data_counts = df_trim["Bridge_Cat"].value_counts()


sns.set_theme(style="whitegrid")
colors = sns.color_palette('pastel')[0:len(data_counts)] 


plt.figure(figsize=(5, 5))
plt.pie(
    data_counts, 
    labels=data_counts.index, 
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)

# ۵. افزودن عنوان
plt.title(f'Distribution of {"Bridge_Cat"}', fontsize=16, pad=20)

# نمایش نمودار
plt.show()

# %%
plt.figure(figsize=(8,5))
df_trim["Age"].hist(bins=20)
plt.title("Bridge Age Distribution")
plt.xlabel("Age")
plt.ylabel("Count")
plt.show()

# %%
metrics = [
    'current_Cond_Rat_Deck',
    'current_Cond_Rat_Super',
    'current_Cond_Rat_Sub',
]

fig, axes = plt.subplots(
    1, 3,
    figsize=(18, 5)
)

axes = axes.flatten()

for i, metric in enumerate(metrics):
    sns.histplot(
        data=df_trim,
        x=metric,
        bins=20,
        kde=True,
        ax=axes[i]
    )
    
    axes[i].set_xlabel(metric)
    axes[i].set_ylabel("Count")

plt.tight_layout()
plt.show()

# %%
plt.figure(figsize=(8,5))
df_trim["BCI"].hist(bins=20)
plt.title("Bridge BCI Distribution")
plt.xlabel("BCI")
plt.ylabel("Count")
plt.show()

# %%
plt.figure(figsize=(8,5))
df_trim["Condition"].hist(bins=20)
plt.title("Bridge Condition Distribution")
plt.xlabel("Condition")
plt.ylabel("Count")
plt.show()

# %%
plt.figure(figsize=(8,5))

plt.scatter(
    df_trim["Age"],
    df_trim["BCI"]
)

plt.xlabel("Age")
plt.ylabel("Condition")

plt.title(
    "Age vs Condition"
)

plt.show()

# %%
def normalize(series):
    return (
        (series - series.min()) /
        (series.max() - series.min())
    ) * 100

# %%
df_trim["Condition_Score"] = normalize(
    100 - df_trim["Condition"]
)

df_trim["Age_Score"] = normalize(
    df_trim["Age"]
)

df_trim["Traffic_Score"] = normalize(
    df_trim["Traffic_Volume"]
)

df_trim["Cost_Score"] = normalize(
    df_trim["Replacement_Cost"]
)

# %%
df_trim["Priority Score"] = (
      0.40 * df_trim["Condition_Score"]
    + 0.30 * df_trim["Traffic_Score"]
    + 0.20 * df_trim["Age_Score"]
    + 0.10 * df_trim["Cost_Score"]
)

# %%
top10 = (
    df_trim.sort_values(
        "Priority Score",
        ascending=False
    )
    .head(10)
)

display(
    top10[
        [
            "Structure_ID",
            "Priority Score",
            "Condition",
            "Age",
            "Traffic_Volume"
        ]
    ]
)

df_trim["Bridge_condition_Cat"] = np.where(
    df_trim["BCI"] >= 80, "Good",
    np.where(df_trim["BCI"] >= 50, "Fair", "Poor")
)

display(df_trim.sort_values("BCI").head(20))
