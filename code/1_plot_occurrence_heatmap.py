from folium.plugins import HeatMap
import folium
import ast
import pandas as pd
from pathlib import Path
import textwrap


def plot_interactive_heatmap(csv_files, notes_file, output_file, dark=False):
    """
    Creates an interactive heatmap of aggregated aphia counts per location.
    If dark=True, uses ESRI Dark Gray Canvas and a gradient heatmap with logo.
    Adds title and a single merged box (notes first, then total observations and dasids).
    """

    # --- Map style selection ---
    if dark:
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        attribution = "Tiles © Esri — Esri, DeLorme, NAVTEQ"
        m = folium.Map(location=[0, 0], zoom_start=2, tiles=tiles, attr=attribution)
        heatmap_gradient = {0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
    else:
        m = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB positron")
        heatmap_gradient = None  # default

    # --- Load and process CSVs ---
    all_rows = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df["aphiaid"] = df["aphiaid"].apply(lambda x: ast.literal_eval(x))
        df["aphia_count"] = df["aphiaid"].apply(len)
        all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True)

    # Aggregate by lat/lon
    agg = combined.groupby(["latitude", "longitude"], as_index=False).agg({"aphia_count": "sum"})
    total_obs = agg["aphia_count"].sum()

    # Prepare heatmap data
    heat_data = [[row.latitude, row.longitude, row.aphia_count] for _, row in agg.iterrows()]
    HeatMap(heat_data, radius=10, max_zoom=15, gradient=heatmap_gradient).add_to(m)

    # --- Title HTML ---
    title_html = f'''
            <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                        z-index:9999; text-align:center; font-size:20px; color:white;">
                <img src="https://dto-bioflow.eu/themes/custom/skeleton/logo.svg"
                     height="40px" style="vertical-align: middle;">
                <b> Biological observations onboarded in DTO-Bioflow</b>
            </div>
        '''
    m.get_root().html.add_child(folium.Element(title_html))

    # --- Prepare dasid list ---
    dasids = []
    for csv_file in csv_files:
        name = Path(csv_file).stem
        if "dasid_" in name:
            try:
                dasid = name.split("dasid_")[1]
                dasids.append(dasid)
            except:
                pass

    if dasids:
        dasid_string = ", ".join(sorted(set(dasids)))
        wrapped_dasids = textwrap.fill(dasid_string, width=100)
    else:
        wrapped_dasids = "No dasids available."

    # --- Load notes (HTML) ---
    notes_path = Path(notes_file)
    if notes_path.exists():
        notes_html = notes_path.read_text(encoding="utf-8")
    else:
        print(f"⚠️ Notes file {notes_file} not found. Skipping notes section.")
        notes_html = "<i>No notes provided.</i>"

    # --- Combined Notes + Legend box ---
    merged_box_html = f'''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 420px; height: auto;
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; opacity:0.85;
                    padding: 10px; overflow:auto;">

            <div style="margin-bottom: 10px;">
                <b>DTO-Bioflow</b><br>
                {notes_html}
            </div>

            <hr style="border:1px solid #ccc;">

            <b>Total observations:</b> {total_obs}<br><br>

            <b>Dasids:</b><br>
            {wrapped_dasids}

        </div>
    '''

    m.get_root().html.add_child(folium.Element(merged_box_html))

    # Save map
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_file)
    print(f"✅ Saved interactive heatmap to {output_file}")



# ------------------ MAIN ------------------

if __name__ == "__main__":

    # --- INPUT DIRECTORIES ---
    dir_call1 = Path("../data/output_call1")
    csv_files_call1 = sorted(list(dir_call1.glob("*.csv")))

    dir_sensor = Path("../data/output_sensor_data")
    csv_files_sensor = sorted(list(dir_sensor.glob("*.csv")))

    # Combined
    csv_files_combined = sorted(csv_files_call1 + csv_files_sensor)

    notes = "../sources/aggregate_description.html"

    # ------------------------------
    #   CALL1 ONLY
    # ------------------------------
    plot_interactive_heatmap(
        csv_files_call1,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_call1.html",
        dark=False
    )

    plot_interactive_heatmap(
        csv_files_call1,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_call1_dark.html",
        dark=True
    )

    # ------------------------------
    #   SENSOR DATA ONLY
    # ------------------------------
    plot_interactive_heatmap(
        csv_files_sensor,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_sensor.html",
        dark=False
    )

    plot_interactive_heatmap(
        csv_files_sensor,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_sensor_dark.html",
        dark=True
    )

    # ------------------------------
    #   COMBINED CALL1 + SENSOR
    # ------------------------------
    plot_interactive_heatmap(
        csv_files_combined,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_combined.html",
        dark=False
    )

    plot_interactive_heatmap(
        csv_files_combined,
        notes_file=notes,
        output_file="../plots/aggregated_heatmap_combined_dark.html",
        dark=True
    )

    # Dark version
    plot_interactive_heatmap(
        csv_files_combined,
        notes_file="../sources/aggregate_description.html",
        output_file="../plots/aggregated_heatmap_dark.html",
        dark=True
    )
