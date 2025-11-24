import pandas as pd
import ast
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import textwrap


def extract_aphia_from_csvs(csv_files):
    """Extract and flatten all AphiaIDs from a list of CSV files."""
    all_ids = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )
        ids = [aid for sub in df["aphiaid"] for aid in sub]
        all_ids.extend(ids)
    return all_ids


def extract_dasids(csv_files):
    """Extract DASID numbers from CSV filenames."""
    return sorted([Path(f).stem.split("_")[-1] for f in csv_files])


def plot_aphia_pie(csv_files, output_dir, title="", top_n=15, add_dasid_box=False):
    """
    Create a pie plot of AphiaID distribution from a list of CSV files.

    Parameters
    ----------
    csv_files : list of Paths
    output_dir : str or Path
    title : str
    top_n : int
    add_dasid_box : bool  -> add DASID text window (for combined pies)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    aphia_list = extract_aphia_from_csvs(csv_files)
    total = len(aphia_list)

    if total == 0:
        print("⚠️ No AphiaIDs found — skipping pie plot.")
        return

    counts = Counter(aphia_list)
    most_common = counts.most_common(top_n)

    labels = [str(aid) for aid, _ in most_common]
    values = [count for _, count in most_common]

    if len(counts) > top_n:
        other_count = total - sum(values)
        labels.append("Other")
        values.append(other_count)

    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % cmap.N) for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        values,
        colors=colors,
        startangle=90,
        wedgeprops=dict(edgecolor='w'),
        autopct=lambda pct: f"count: {int(round(pct * total / 100))}",
        textprops={'color': 'black', 'fontsize': 10},
    )

    ax.legend(labels, title="AphiaID", bbox_to_anchor=(1, 0.5), loc="center left")

    if not title:
        title = "AphiaID Distribution"
    ax.set_title(title, fontsize=14)

    # ----------------------
    # ADD DASID TEXT WINDOW
    # ----------------------
    if add_dasid_box:
        dasids = extract_dasids(csv_files)
        dasid_text = ", ".join(dasids)

        # Wrap text to fixed width (60 chars per line)
        wrapped_text = textwrap.fill(dasid_text, width=100)

        ax.text(
            0.02, 0.02,
            f"DASIDs:\n{wrapped_text}",
            transform=ax.transAxes,
            va="bottom",
            ha="left",
            fontsize=9,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="black",
                      linewidth=0.5)
        )

    out_file = output_dir / f"{title.replace(' ', '_').lower()}.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved pie chart: {out_file}  (total={total})")


def plot_aphia_per_csv(csv_files, output_dir, top_n=15):
    """
    Plot AphiaID distribution for each CSV file separately.
    (No DASID box here — only individual pies)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )
        dasid = Path(csv_file).stem.split("_")[-1]

        plot_aphia_pie(
            [csv_file],
            output_dir=output_dir,
            title=f"AphiaID Distribution DASID {dasid}",
            top_n=top_n,
            add_dasid_box=False   # individual → NO textbox
        )


if __name__ == "__main__":
    output_csv_dir1 = Path("../data/output_call1")
    output_csv_dir2 = Path("../data/output_sensor_data")

    csv_files1 = sorted(output_csv_dir1.glob("*.csv"))
    csv_files2 = sorted(output_csv_dir2.glob("*.csv"))
    csv_files = csv_files1 + csv_files2

    # ---- Combined pies (WITH DASID text window) ----
    plot_aphia_pie(csv_files,
                   "../plots/",
                   title="aphia_observation_and_sensor",
                   add_dasid_box=True)

    plot_aphia_pie(csv_files1,
                   "../plots/",
                   title="aphia_observation_data",
                   add_dasid_box=True)

    plot_aphia_pie(csv_files2,
                   "../plots/",
                   title="aphia_sensor_data",
                   add_dasid_box=True)

    # ---- Individual pies (NO DASID text window) ----
    plot_aphia_per_csv(csv_files, "../plots/aphia_per_dasid/")
