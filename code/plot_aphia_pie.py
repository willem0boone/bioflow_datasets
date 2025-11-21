import pandas as pd
import ast
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import requests


def plot_aphia_pie(aphia_list, output_file, title="", top_n=15):
    """
    Plot a pie chart of AphiaID distribution.

    - Counts are shown directly on the slices: 'count: {count}'
    - Legend only shows the AphiaID
    """
    total = len(aphia_list)
    if total == 0:
        print(f"⚠️ No AphiaIDs to plot for {output_file}")
        return

    counts = Counter(aphia_list)
    most_common = counts.most_common(top_n)
    top_labels = [str(aid) for aid, _ in most_common]
    top_counts = [count for _, count in most_common]

    # Handle "Other"
    if len(counts) > top_n:
        other_count = total - sum(top_counts)
        top_labels.append("Other")
        top_counts.append(other_count)

    # Color map
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % cmap.N) for i in range(len(top_labels))]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        top_counts,
        colors=colors,
        startangle=90,
        wedgeprops=dict(edgecolor='w'),  # full pie, no width
        autopct=lambda pct: f"count: {int(round(pct*total/100))}",  # show counts
        textprops={'color': 'black', 'fontsize': 10}
    )

    # Legend: only AphiaIDs
    ax.legend(wedges, top_labels, title="AphiaID", bbox_to_anchor=(1, 0.5),
              loc="center left")

    ax.set_title(title, fontsize=14)

    # Save
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved pie chart to {output_file} (total observations: {total})")


def plot_aphia_per_csv(csv_files, output_dir, top_n=15):
    """Plot AphiaID distribution per CSV and for all merged."""
    all_aphia = []

    for csv_file in csv_files:
        dasid = Path(csv_file).stem.split("_")[-1]
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        aphia_list = [aid for sublist in df["aphiaid"] for aid in sublist]

        # Plot per CSV
        plot_aphia_pie(
            aphia_list,
            output_file=Path(output_dir) / f"aphia/aphia_distribution_dasid_{dasid}.png",
            title=f"AphiaID Distribution for DASID {dasid}",
            top_n=top_n
        )

        all_aphia.extend(aphia_list)

    # Plot combined
    plot_aphia_pie(
        all_aphia,
        output_file=Path(output_dir) / f"aphia_distribution_all.png",
        title="AphiaID Distribution Across All Datasets",
        top_n=top_n
    )


if __name__ == "__main__":
    output_csv_dir1 = Path("../data/output_call1")
    output_csv_dir2 = Path("../data/output_wp3")

    csv_files1 = sorted(output_csv_dir1.glob("*.csv"))
    csv_files2 = sorted(output_csv_dir2.glob("*.csv"))

    csv_files = csv_files1 + csv_files2

    plot_aphia_per_csv(csv_files, output_dir="../plots/")

