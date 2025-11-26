from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------

def read_csv_files(csv_files):
    """Read and combine CSV files into a DataFrame, sorted by observationdate."""
    all_data = []
    for f in csv_files:
        df = pd.read_csv(f, parse_dates=['observationdate'])
        all_data.append(df)
    if all_data:
        data = pd.concat(all_data, ignore_index=True)
        return data.sort_values('observationdate')
    return pd.DataFrame(columns=['observationdate'])


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def first_nonzero_index(series):
    nz = np.flatnonzero(series.values > 0)
    return nz[0] if len(nz) else None


# -----------------------------------------------------------
# Fixed-axis helper
# -----------------------------------------------------------

def get_global_axes_limits(*datasets):
    """Return global x-range (dates) and y-range (final cumulative max)."""
    # concatenate all observationdate columns
    dates = pd.concat([d['observationdate'] for d in datasets])

    x_min = dates.min()
    x_max = dates.max()

    # cumulative maximum
    ymax = 0
    for d in datasets:
        if not d.empty:
            counts = d.groupby('observationdate').size().cumsum()
            ymax = max(ymax, counts.max())

    # add a small epsilon to avoid log issues
    if ymax == 0:
        ymax = 1

    return x_min, x_max, ymax


# -----------------------------------------------------------
# Plot single frame
# -----------------------------------------------------------

def plot_single_frame(data, year, out_file, x_min, x_max, y_max,
                      color='tab:blue', label='Data'):

    years = np.arange(x_min.year, x_max.year + 1)
    year_dates = pd.to_datetime([f"{y}-01-01" for y in years])

    yearly_counts = data['observationdate'].dt.year.value_counts().sort_index()
    yearly_counts = yearly_counts.reindex(years, fill_value=0)

    cum = yearly_counts.cumsum()

    visible_mask = years <= year
    visible_dates = year_dates[visible_mask]
    visible_cum = cum[visible_mask]

    # The last value is the cumulative count in this frame
    current_obs = int(visible_cum.iloc[-1]) if len(visible_cum) else 0

    plt.figure(figsize=(12, 6))

    if len(visible_dates) > 0:
        plt.plot(visible_dates, visible_cum, color=color, label=label)
        plt.fill_between(visible_dates, 0, visible_cum, color=color, alpha=0.3)

    plt.xlim(pd.to_datetime(x_min), pd.to_datetime(x_max))
    plt.ylim(0, y_max)

    plt.xlabel('Observation Date')
    plt.ylabel('Cumulative Count')
    plt.title(f"{year} – observations: {current_obs}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()

# -----------------------------------------------------------
# Plot combined frame
# -----------------------------------------------------------


def plot_combined_frame(data1, data2,
                        year,
                        out_file,
                        x_min, x_max, y_max,
                        color1='tab:blue',
                        color2='tab:orange',
                        label1='Set1',
                        label2='Set2',
                        log=False):

    years = np.arange(x_min.year, x_max.year + 1)
    year_dates = pd.to_datetime([f"{y}-01-01" for y in years])

    y1 = data1['observationdate'].dt.year.value_counts().sort_index().reindex(years, fill_value=0)
    y2 = data2['observationdate'].dt.year.value_counts().sort_index().reindex(years, fill_value=0)

    c1 = y1.cumsum()
    c2 = y2.cumsum()
    stacked = c1 + c2

    visible_mask = years <= year
    vis_dates = year_dates[visible_mask]
    vis_c1 = c1[visible_mask]
    vis_stack = stacked[visible_mask]

    # The final stacked count
    current_obs = int(vis_stack.iloc[-1]) if len(vis_stack) else 0

    plt.figure(figsize=(12, 6))

    if len(vis_dates) > 0:
        plt.plot(vis_dates, vis_c1, color=color1, label=label1)
        plt.plot(vis_dates, vis_stack, color=color2, label=label2)

        plt.fill_between(vis_dates, 0, vis_c1, color=color1, alpha=0.3)
        plt.fill_between(vis_dates, vis_c1, vis_stack, color=color2, alpha=0.3)

    plt.xlim(pd.to_datetime(x_min), pd.to_datetime(x_max))

    if log:
        plt.yscale('log')
        plt.ylim(1, max(1, y_max))
    else:
        plt.ylim(0, y_max)

    plt.xlabel('Observation Date')
    plt.ylabel('Cumulative Count (stacked)')
    plt.title(f"{year} – observations: {current_obs}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
# -----------------------------------------------------------
# FRAME GENERATORS
# -----------------------------------------------------------

def generate_frames_single(data, dataset_name, base_outdir):
    print(f"[START] Generating frames for {dataset_name}...")

    if data.empty:
        print(f"[SKIP] No data for {dataset_name}.")
        return

    years = list(range(
        data['observationdate'].dt.year.min(),
        data['observationdate'].dt.year.max() + 1
    ))

    outdir = base_outdir / f"source_{dataset_name}"
    ensure_dir(outdir)

    x_min, x_max, y_max = get_global_axes_limits(data)

    for y in years:
        out_file = outdir / f"year_{y}.png"
        plot_single_frame(data, year=y, out_file=out_file,
                          x_min=x_min, x_max=x_max, y_max=y_max,
                          color='tab:blue', label=dataset_name)

    print(f"[DONE] {dataset_name}: {len(years)} frames saved in {outdir}")


def generate_frames_combined(data1, data2,
                             name1, name2,
                             combined_name,
                             base_outdir,
                             log=False):
    print(f"[START] Generating combined frames for {combined_name}...")

    if data1.empty and data2.empty:
        print(f"[SKIP] Both datasets empty.")
        return

    years = list(range(
        min(data1['observationdate'].dt.year.min(),
            data2['observationdate'].dt.year.min()),
        max(data1['observationdate'].dt.year.max(),
            data2['observationdate'].dt.year.max()) + 1
    ))

    outdir = base_outdir / f"source_{combined_name}"
    ensure_dir(outdir)

    x_min, x_max, y_max = get_global_axes_limits(data1, data2)

    for y in years:
        out_file = outdir / f"year_{y}.png"
        plot_combined_frame(
            data1, data2, year=y, out_file=out_file,
            x_min=x_min, x_max=x_max, y_max=y_max,
            color1='tab:blue', color2='tab:orange',
            label1=name1, label2=name2, log=log
        )

    print(f"[DONE] {combined_name}: {len(years)} frames saved in {outdir}")


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------

if __name__ == "__main__":
    csv_dir1 = Path("../data/output_call1")
    csv_dir2 = Path("../data/output_sensor_data")

    out_dir = Path("../plots/timeline")

    data_obs = read_csv_files(sorted(csv_dir1.glob("*.csv")))
    data_sen = read_csv_files(sorted(csv_dir2.glob("*.csv")))

    generate_frames_single(data_obs, "observations", out_dir)
    generate_frames_single(data_sen, "sensor_observations", out_dir)

    generate_frames_combined(
        data_sen, data_obs,
        name1="sensor_observations",
        name2="observations",
        combined_name="all_combined",
        base_outdir=out_dir,
        log=False
    )

    generate_frames_combined(
        data_sen, data_obs,
        name1="sensor_observations",
        name2="observations",
        combined_name="all_combined_log",
        base_outdir=out_dir,
        log=True
    )


