from folium.plugins import HeatMap
import folium
import ast
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import contextily as ctx
from pathlib import Path


def plot_unique_locations(csv_files, output_file):

    output_file = Path(output_file)
    subdir = output_file.parent / "map_per_dasid"
    subdir.mkdir(parents=True, exist_ok=True)

    # Load world once
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres")).to_crs(epsg=3857)

    # Hard-coded Web Mercator vertical limits
    YMIN = -9074929
    YMAX = +16847944

    total_obs_all = 0
    total_taxa_all = set()
    combined_gdf_list = []

    for csv_file in csv_files:

        dasid = Path(csv_file).stem.split("_")[-1]

        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(lambda x: eval(x) if isinstance(x, str) else [])

        obs_count = df["aphiaid"].apply(len).sum()
        unique_taxa = set(a for sub in df["aphiaid"] for a in sub)

        # collapse duplicates by lat/lon
        df_unique = df.groupby(["latitude", "longitude"]).agg({
            "aphiaid": lambda x: [a for sub in x for a in sub]
        }).reset_index()
        df_unique["obs_count"] = df_unique["aphiaid"].apply(len)

        gdf = gpd.GeoDataFrame(
            df_unique,
            geometry=gpd.points_from_xy(df_unique.longitude, df_unique.latitude),
            crs="EPSG:4326"
        ).to_crs(3857)

        combined_gdf_list.append(gdf)

        # -------------------------------------------------------------
        # INDIVIDUAL MAP
        # -------------------------------------------------------------
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])

        gdf.plot(ax=ax, markersize=10, color=(1, 0, 0, 0.8))

        # get bounds
        x_min, y_min, x_max, y_max = gdf.total_bounds

        # square extent
        dx = x_max - x_min
        dy = y_max - y_min

        min_side = 150000  # minimum 150 km square
        side = max(dx, dy, min_side)

        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2

        x_left  = cx - side/2
        x_right = cx + side/2

        y_bot   = max(cy - side/2, YMIN)
        y_top   = min(cy + side/2, YMAX)

        ax.set_xlim(x_left, x_right)
        ax.set_ylim(y_bot, y_top)
        ax.set_aspect("equal")

        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # REMOVE ticks, tick labels, and axis labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_axis_off()   # also hides axis frame

        ax.set_title(f"DASID {dasid}\nObs: {obs_count} | Taxa: {len(unique_taxa)}")

        # -------------------------------------------------------------
        # INSET MAP (lower-left, padded red rectangle)
        # -------------------------------------------------------------
        inset = inset_axes(ax, width="28%", height="28%", loc="lower left", borderpad=1.2)

        world.boundary.plot(ax=inset, linewidth=0.4, edgecolor="gray")

        inset.set_xlim(-20037508.34, 20037508.34)
        inset.set_ylim(YMIN, YMAX)
        inset.set_aspect("equal")

        # Draw RED RECTANGLE with padding
        pad_inset = side * 0.15

        rect = Rectangle(
            (x_left - pad_inset, y_bot - pad_inset),
            side + 2*pad_inset,
            (y_top - y_bot) + 2*pad_inset,
            linewidth=2.0,
            edgecolor="red",
            facecolor="none"
        )
        inset.add_patch(rect)

        # REMOVE ticks / labels on inset
        inset.set_xticks([])
        inset.set_yticks([])
        inset.set_xlabel("")
        inset.set_ylabel("")
        inset.set_frame_on(True)

        outfile = subdir / f"dasid_{dasid}_map.png"
        fig.savefig(outfile, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Saved individual map: {outfile}")

        total_obs_all += obs_count
        total_taxa_all.update(unique_taxa)

    # -------------------------------------------------------------
    # COMBINED MAP
    # -------------------------------------------------------------
    combined_gdf = pd.concat(combined_gdf_list, ignore_index=True)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])

    combined_gdf.plot(ax=ax, markersize=2, color=(1, 0, 0, 0.8))

    ax.set_xlim(-20037508.34, 20037508.34)
    ax.set_ylim(YMIN, YMAX)
    ax.set_aspect("equal")

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    # REMOVE all x/y labels and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_axis_off()

    ax.set_title(
        f"Observation Locations (All Datasets)\n"
        f"Obs: {total_obs_all} | Taxa: {len(total_taxa_all)}"
    )

    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved combined map: {output_file}")


def find_bad_aphiaid_entries(csv_files, column="aphiaid", max_errors=10):
    """
    Scan CSVs for rows where ast.literal_eval() fails on the aphiaid column.

    Parameters
    ----------
    csv_files : list or Path
        List of CSV file paths to check.
    column : str
        Column name to validate (default: 'aphiaid').
    max_errors : int
        Max number of bad rows to show per file.

    Returns
    -------
    bad_summary : dict
        Dictionary mapping CSV file → list of (row_index, bad_value, error_message).
    """

    bad_summary = {}

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"⚠️ Could not read {csv_file}: {e}")
            continue

        if column not in df.columns:
            print(f"⚠️ Column '{column}' not found in {csv_file}")
            continue

        bad_rows = []
        for idx, val in df[column].items():
            if pd.isna(val):
                continue  # skip true NaN
            if isinstance(val, list):
                continue  # already parsed
            try:
                ast.literal_eval(str(val))
            except Exception as e:
                bad_rows.append((idx, val, str(e)))
                if len(bad_rows) >= max_errors:
                    break

        if bad_rows:
            bad_summary[csv_file] = bad_rows
            print(
                f"\n🚨 Found {len(bad_rows)} bad aphiaid entries in: {csv_file}")
            for i, (idx, val, err) in enumerate(bad_rows):
                print(f"   [{idx}] {val!r} → {err}")
        else:
            print(f"✅ {csv_file} is clean — all aphiaid values parsed OK")

    print(
        f"\n🔍 Summary: {len(bad_summary)} file(s) have malformed aphiaid entries.")
    return bad_summary


if __name__ == "__main__":
    dir_call1 = Path("../data/output_call1")
    csv_files_call1 = list(dir_call1.glob("*.csv"))

    dir_wp3 = Path("../data/output_wp3")
    csv_files_wp3 = list(dir_wp3.glob("*.csv"))

    #find_bad_aphiaid_entries(csv_files_wp3)

    csv_files = csv_files_call1 + csv_files_wp3

    csv_files.sort()  # Optional: sort by name/dasid

    plot_unique_locations(csv_files=csv_files,
                          output_file="../plots/unique_locations_map.png")

    # Generate all plots
    # plot_interactive_heatmap(csv_files,
    #                          notes_file="aggregate_description.html",
    #                          output_file="../plots/aggregated_heatmap.html")
    #
    # plot_interactive_heatmap_dark(csv_files,
    #                          notes_file="aggregate_description.html",
    #                          output_file="../plots/aggregated_heatmap_dark.html")



