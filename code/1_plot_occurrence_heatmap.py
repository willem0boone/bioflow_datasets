from folium.plugins import HeatMap
import folium
import ast
import pandas as pd
from pathlib import Path


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



if __name__ == "__main__":
    dir_call1 = Path("../data/output_call1")
    csv_files_call1 = list(dir_call1.glob("*.csv"))

    dir_wp3 = Path("../data/output_wp3")
    csv_files_wp3 = list(dir_wp3.glob("*.csv"))

    #find_bad_aphiaid_entries(csv_files_wp3)

    csv_files = csv_files_call1 + csv_files_wp3
    csv_files.sort()  # Optional: sort by name/dasid

    # Generate all plots
    plot_interactive_heatmap(csv_files,
                             notes_file="../sources/aggregate_description.html",
                             output_file="../plots/aggregated_heatmap.html")

    plot_interactive_heatmap_dark(csv_files,
                                  notes_file="../sources/aggregate_description.html",
                                  output_file="../plots/aggregated_heatmap_dark.html")



