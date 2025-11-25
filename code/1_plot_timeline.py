from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def read_csv_files(csv_files):
    """Read and combine CSV files into a single DataFrame, sorted by observationdate."""
    all_data = []
    for f in csv_files:
        df = pd.read_csv(f, parse_dates=['observationdate'])
        all_data.append(df)
    if all_data:
        data = pd.concat(all_data, ignore_index=True)
        return data.sort_values('observationdate')
    return pd.DataFrame(columns=['observationdate'])

def plot_timeline_single(data, color='tab:blue', label='Data'):
    """Plot a single timeline with filled area under the curve."""
    if data.empty:
        print(f"No data to plot for {label}.")
        return
    y = np.arange(len(data))
    plt.figure(figsize=(12, 6))
    plt.plot(data['observationdate'], y, color=color, label=label)
    plt.fill_between(data['observationdate'], 0, y, color=color, alpha=0.3)
    plt.xlabel('Observation Date')
    plt.ylabel('Observation Index')
    plt.title(f'Timeline of {label}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_timeline_combined(data1, data2, color1='tab:blue', color2='tab:orange', label1='CSV Set 1', label2='CSV Set 2'):
    """Plot two timelines stacked on top of each other with filled areas."""
    plt.figure(figsize=(12, 6))

    if not data1.empty:
        y1 = np.arange(len(data1))
        plt.plot(data1['observationdate'], y1, color=color1, label=label1)
        plt.fill_between(data1['observationdate'], 0, y1, color=color1, alpha=0.3)

    if not data2.empty:
        offset = len(data1)
        y2 = np.arange(len(data2)) + offset
        plt.plot(data2['observationdate'], y2, color=color2, label=label2)
        plt.fill_between(data2['observationdate'], offset, y2, color=color2, alpha=0.3)

    plt.xlabel('Observation Date')
    plt.ylabel('Observation Index (stacked)')
    plt.title('Stacked Timeline of Observations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Directories
    output_csv_dir1 = Path("../data/output_call1")
    output_csv_dir2 = Path("../data/output_sensor_data")

    csv_files1 = sorted(output_csv_dir1.glob("*.csv"))
    csv_files2 = sorted(output_csv_dir2.glob("*.csv"))

    # Read CSVs
    data1 = read_csv_files(csv_files1)
    data2 = read_csv_files(csv_files2)

    # Plot first CSV set
    plot_timeline_single(data1, color='tab:blue', label='CSV Set 1')

    # Plot second CSV set
    plot_timeline_single(data2, color='tab:orange', label='CSV Set 2')

    # Plot combined stacked timeline
    plot_timeline_combined(data1, data2)


