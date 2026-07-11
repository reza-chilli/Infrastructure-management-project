import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")


def plot_bridge_category_distribution(
    df,
    figsize=(3.2, 3.2),
    title_fontsize=10,
    label_fontsize=8,
    pct_fontsize=7,
):
    data_counts = df["Bridge_Cat"].value_counts()
    colors = sns.color_palette("pastel", n_colors=len(data_counts))

    fig, ax = plt.subplots(figsize=figsize, dpi=140)

    wedges, _, autotexts = ax.pie(
        data_counts,
        labels=None,  # labels را از روی نمودار برمی‌داریم تا شلوغ نشود
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
        textprops={"fontsize": pct_fontsize, "color": "black"},
        pctdistance=0.7,
    )

    ax.set_title("Distribution of Bridge_Cat", fontsize=title_fontsize, pad=10)

    ax.legend(
        wedges,
        data_counts.index,
        title="Bridge_Cat",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=label_fontsize,
        title_fontsize=label_fontsize,
        frameon=False,
    )

    fig.tight_layout()
    return fig


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


def plot_current_condition_ratings(df):
    metrics = [
        "current_Cond_Rat_Deck",
        "current_Cond_Rat_Super",
        "current_Cond_Rat_Sub",
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
            x=metric,
            bins=20,
            kde=True,
            ax=axes[i]
        )

        axes[i].set_xlabel(metric)
        axes[i].set_ylabel("Count")

    fig.tight_layout()

    return fig


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


def plot_condition_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 5))

    df["Condition"].hist(
        bins=20,
        ax=ax
    )

    ax.set_title("Bridge Condition Distribution")
    ax.set_xlabel("Condition")
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
