from folium.plugins import HeatMap
import folium
import pandas as pd
import geopandas as gpd
import contextily as ctx
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import ast
from shapely.geometry import box


def plot_unique_locations(csv_files, output_file):
    """
    Plots unique lat/lon points from multiple CSV files.

    - Combined map saved as PNG (output_file)
    - Each CSV plotted separately in 'map_per_dasid'
    - Individual maps: dark red, larger dots, mini-world overview
    - Combined map: dark red, smaller dots, no legend
    - Titles include total observations and unique AphiaIDs
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    dark_red = (1.0, 0.0, 0.0)  # RGB normalized for matplotlib
    legend_elements = []

    # Subfolder for individual maps
    output_file = Path(output_file)
    subdir = output_file.parent / "map_per_dasid"
    subdir.mkdir(parents=True, exist_ok=True)

    total_obs = 0
    all_aphia = set()

    for csv_file in csv_files:
        dasid = Path(csv_file).stem.split("_")[-1]
        df = pd.read_csv(csv_file)

        # Parse aphiaid column
        try:
            df["aphiaid"] = df["aphiaid"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else []
            )
        except Exception as e:
            print(f"⚠️ Error parsing aphiaid column in {csv_file}: {e}")
            continue

        aphia_list = [aid for sublist in df["aphiaid"] for aid in sublist]
        taxa_count = len(set(aphia_list))
        obs_count = len(df)
        total_obs += obs_count
        all_aphia.update(aphia_list)

        df_unique = df.drop_duplicates(subset=["latitude", "longitude"])
        print(f"DASID {dasid}: {len(df_unique)} unique lat/lon points | "
              f"Obs: {obs_count:,} | Taxa: {taxa_count:,}")

        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df_unique,
            geometry=gpd.points_from_xy(df_unique.longitude, df_unique.latitude),
            crs="EPSG:4326"
        ).to_crs(epsg=3857)

        # ------------------ Individual map ------------------
        fig_ind, ax_ind = plt.subplots(figsize=(10, 6))
        ax_ind.scatter(
            gdf.geometry.x,
            gdf.geometry.y,
            s=25,  # larger dots
            c=[dark_red],
            marker='o',
            edgecolors='none',
            alpha=0.8
        )

        ctx.add_basemap(ax_ind, source=ctx.providers.OpenStreetMap.Mapnik)
        ax_ind.set_aspect('equal')
        ax_ind.set_title(
            f"DASID {dasid}\nOccurrences: {obs_count:,} | Taxa: {taxa_count:,}",
            fontsize=13, pad=10
        )
        ax_ind.set_xlabel("Longitude")
        ax_ind.set_ylabel("Latitude")
        ax_ind.margins(0.02)

        # --- Add inset world map correctly ---
        axins = inset_axes(ax_ind, width="20%", height="20%",
                           loc='lower right', borderpad=1)

        # Load world map (EPSG:4326)
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        # Convert main map bbox back to EPSG:4326 for inset
        # Convert main map bbox back to EPSG:4326 for inset
        x_min, y_min, x_max, y_max = gdf.total_bounds  # EPSG:3857
        bbox_geom = gpd.GeoDataFrame(
            geometry=[box(x_min, y_min, x_max, y_max)],
            crs="EPSG:3857"
        ).to_crs(epsg=4326)

        # Plot world
        world.plot(ax=axins, color='lightgrey', edgecolor='black')

        # Plot bbox in red
        bbox_geom.boundary.plot(ax=axins, edgecolor='red', linewidth=2)

        # Clean up inset ticks
        axins.set_xticks([])
        axins.set_yticks([])
        axins.set_xlim(-180, 180)
        axins.set_ylim(-90, 90)

        single_file = subdir / f"dasid_{dasid}_map.png"
        plt.savefig(single_file, dpi=600, bbox_inches="tight")
        plt.close(fig_ind)
        print(f"🗺️ Saved individual map: {single_file}")

        # ------------------ Add points to combined map ------------------
        ax.scatter(
            gdf.geometry.x,
            gdf.geometry.y,
            s=5,  # smaller dots for combined
            c=[dark_red],
            marker='.',
            edgecolors='none',
            alpha=1
        )

    # ------------------ Combined map ------------------
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.set_aspect('equal')
    ax.set_title(
        f"Observation Locations (All Datasets)\nOccurrences: {total_obs:,} | Taxa: {len(all_aphia):,}",
        fontsize=14, pad=12
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.margins(0.02)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=1000, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved combined PNG map to {output_file}")


# OLD code
# def plot_unique_locations(csv_files, output_file):
#     """
#     Plots unique lat/lon points from multiple CSV files.
#
#     - Combined map saved as PNG (output_file)
#     - Each CSV also plotted separately in subfolder 'map_per_dasid'
#     - Each CSV gets a distinct color (tab20 colormap)
#     - Basemap: OpenStreetMap (bright, detailed)
#     - Small scatter dots on map
#     - Larger dots in legend for readability
#     """
#     fig, ax = plt.subplots(figsize=(14, 7))
#     cmap = get_cmap("tab20")
#     num_colors = cmap.N
#     legend_elements = []
#
#     # Subfolder for individual maps
#     output_file = Path(output_file)
#     subdir = output_file.parent / "map_per_dasid"
#     subdir.mkdir(parents=True, exist_ok=True)
#
#     for i, csv_file in enumerate(csv_files):
#         dasid = Path(csv_file).stem.split("_")[-1]
#         df = pd.read_csv(csv_file)
#
#         # Keep unique lat/lon
#         df_unique = df.drop_duplicates(subset=["latitude", "longitude"])
#         print(f"DASID {dasid}: {len(df_unique)} unique lat/lon points")
#
#         # Convert to GeoDataFrame (Web Mercator)
#         gdf = gpd.GeoDataFrame(
#             df_unique,
#             geometry=gpd.points_from_xy(df_unique.longitude, df_unique.latitude),
#             crs="EPSG:4326"
#         ).to_crs(epsg=3857)
#
#         color = cmap(i % num_colors)
#
#         # Add to combined plot
#         ax.scatter(
#             gdf.geometry.x,
#             gdf.geometry.y,
#             s=5,
#             c=[color],
#             marker='.',
#             edgecolors='none',
#             alpha=1
#         )
#
#         legend_elements.append(Line2D(
#             [0], [0],
#             marker='o',
#             color='w',
#             label=f"DASID {dasid}",
#             markerfacecolor=color,
#             markersize=8
#         ))
#
#         # --- Create individual map for this CSV ---
#         fig_ind, ax_ind = plt.subplots(figsize=(10, 6))
#         ax_ind.scatter(
#             gdf.geometry.x,
#             gdf.geometry.y,
#             s=10,
#             c=[color],
#             marker='o',
#             edgecolors='none',
#             alpha=0.8
#         )
#         ctx.add_basemap(ax_ind, source=ctx.providers.OpenStreetMap.Mapnik)
#         ax_ind.set_aspect('equal')
#         ax_ind.set_title(f"Observation Locations — DASID {dasid}", fontsize=13, pad=10)
#         ax_ind.set_xlabel("Longitude")
#         ax_ind.set_ylabel("Latitude")
#         ax_ind.margins(0.02)
#
#         single_file = subdir / f"dasid_{dasid}_map.png"
#         plt.savefig(single_file, dpi=600, bbox_inches="tight")
#         plt.close(fig_ind)
#         print(f"🗺️ Saved individual map: {single_file}")
#
#     # --- Combined map ---
#     ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
#     ax.set_aspect('equal')
#     ax.set_title("Observation Locations (All Datasets)", fontsize=14, pad=12)
#     ax.set_xlabel("Longitude")
#     ax.set_ylabel("Latitude")
#     ax.margins(0.02)
#     ax.legend(
#         handles=legend_elements,
#         loc="center left",
#         bbox_to_anchor=(1.05, 0.5),
#         title="Dataset IDs"
#     )
#
#     output_file.parent.mkdir(parents=True, exist_ok=True)
#     plt.savefig(output_file, dpi=1000, bbox_inches="tight")
#     plt.close(fig)
#     print(f"✅ Saved combined PNG map to {output_file}")


def plot_interactive_heatmap(csv_files, notes_file, output_file):
    """
    Creates an interactive heatmap of aggregated aphia counts per location.
    Adds a title, a text box (from an HTML file), and a legend showing total number of observations.
    """
    # Create the map
    m = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB positron")

    # Load and process all CSVs
    all_rows = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(lambda x: ast.literal_eval(x))
        df["aphia_count"] = df["aphiaid"].apply(len)
        all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True)

    # Aggregate by lat/lon, sum aphia counts
    agg = combined.groupby(["latitude", "longitude"], as_index=False).agg({"aphia_count": "sum"})

    # Calculate total observations for legend
    total_obs = agg["aphia_count"].sum()

    # Heatmap expects list of [lat, lon, weight]
    heat_data = [[row.latitude, row.longitude, row.aphia_count] for _, row in agg.iterrows()]
    HeatMap(heat_data, radius=10, max_zoom=15).add_to(m)  # default gradient

    # Add title
    title_html = '''
        <h3 align="center" style="font-size:20px"><b>Biological observations onboarded in DTO-Bioflow</b></h3>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add total observations legend box
    legend_html = f'''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 200px; height: auto;
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; opacity:0.85; padding: 10px;">
            <b>Total observations:</b> {total_obs}
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add notes from external HTML file
    notes_path = Path(notes_file)
    if notes_path.exists():
        with open(notes_path, "r", encoding="utf-8") as f:
            notes_html = f.read()
        text_html = f'''
            <div style="position: fixed;
                        bottom: 150px; left: 50px; width: 300px; height: auto;
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color:white; opacity:0.85; padding: 10px; overflow:auto;">
                {notes_html}
            </div>
        '''
        m.get_root().html.add_child(folium.Element(text_html))
    else:
        print(f"⚠️ Notes file {notes_file} not found. Skipping text box.")

    # Save map
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_file)
    print(f"✅ Saved interactive heatmap to {output_file}")


def plot_interactive_heatmap_dark(csv_files, notes_file, output_file):
    """
    Creates an interactive heatmap of aggregated aphia counts per location.
    Uses ESRI basemap, adds title with logo, a notes box, and a legend showing total observations.
    """
    import folium
    from folium.plugins import HeatMap
    import pandas as pd
    import ast
    from pathlib import Path

    # Use ESRI Dark Gray Canvas for a cleaner, cooler look
    esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
    attribution = "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"

    m = folium.Map(
        location=[0, 0],
        zoom_start=2,
        tiles=esri_tiles,
        attr=attribution
    )

    # Load and process all CSVs
    all_rows = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(lambda x: ast.literal_eval(x))
        df["aphia_count"] = df["aphiaid"].apply(len)
        all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True)

    # Aggregate by lat/lon, sum aphia counts
    agg = combined.groupby(["latitude", "longitude"], as_index=False).agg({"aphia_count": "sum"})

    # Total observations for legend
    total_obs = agg["aphia_count"].sum()

    # Heatmap data
    heat_data = [[row.latitude, row.longitude, row.aphia_count] for _, row in agg.iterrows()]
    HeatMap(heat_data, radius=10, max_zoom=15, gradient={0.2:'blue',0.4:'cyan',0.6:'lime',0.8:'yellow',1.0:'red'}).add_to(m)

    # Add title with logo
    title_html = f'''
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    z-index:9999; text-align:center; font-size:20px; color:white;">
            <img src="https://dto-bioflow.eu/themes/custom/skeleton/logo.svg" height="40px" style="vertical-align: middle;">
            <b> Biological observations onboarded in DTO-Bioflow</b>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add total observations legend
    legend_html = f'''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 200px; height: auto;
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; opacity:0.85; padding: 10px;">
            <b>Total observations:</b> {total_obs}
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add notes box
    notes_path = Path(notes_file)
    if notes_path.exists():
        with open(notes_path, "r", encoding="utf-8") as f:
            notes_html = f.read()
        text_html = f'''
            <div style="position: fixed;
                        bottom: 150px; left: 50px; width: 300px; height: auto;
                        border:2px solid grey; z-index:9999; font-size:14px;
                        background-color:white; opacity:0.85; padding: 10px; overflow:auto;">
                {notes_html}
            </div>
        '''
        m.get_root().html.add_child(folium.Element(text_html))
    else:
        print(f"⚠️ Notes file {notes_file} not found. Skipping text box.")

    # Save map
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_file)
    print(f"✅ Saved interactive heatmap to {output_file}")


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
    dir_call1 = Path("../output_call1")
    csv_files_call1 = list(dir_call1.glob("*.csv"))

    dir_wp3 = Path("../output_wp3")
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



