import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")

# used
def plot_bridge_category_distribution(df):
    data_counts = df["Bridge_Cat"].value_counts()
    colors = sns.color_palette("pastel")[0:len(data_counts)]

    fig, ax = plt.subplots(figsize=(5, 5))

    ax.pie(
        data_counts,
        labels=data_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={
            "edgecolor": "white",
            "linewidth": 2
        }
    )

    ax.set_title(
        f'Distribution of Bridge Categories',
        fontsize=16,
        pad=20
    )

    return fig

# used
def plot_age_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 5))

    df["Age"].hist(
        bins=20,
        ax=ax
    )

    ax.set_title("Bridge Age Distribution")
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")

    return fig

# used
def plot_current_condition_ratings(df):
    metrics = [
        { "title": "Current Deck Condition Rate", "key": "current_Cond_Rat_Deck" },
        { "title": "Current Super Condition Rate", "key": "current_Cond_Rat_Super" },
        { "title": "Current Sub Condition Rate", "key": "current_Cond_Rat_Sub" },
    ]

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(18, 5)
    )

    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        sns.histplot(
            data=df,
            x=metric["key"],
            bins=20,
            kde=True,
            ax=axes[i]
        )

        axes[i].set_xlabel(metric["title"])
        axes[i].set_ylabel("Count")

    fig.tight_layout()

    return fig

# used
def plot_bci_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 5))

    df["BCI"].hist(
        bins=20,
        ax=ax
    )

    ax.set_title("Bridge BCI Distribution")
    ax.set_xlabel("BCI")
    ax.set_ylabel("Count")

    return fig

def plot_age_vs_bci(df):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.scatter(
        df["Age"],
        df["BCI"]
    )

    ax.set_xlabel("Age")
    ax.set_ylabel("Condition")
    ax.set_title("Age vs Condition")

    return fig
