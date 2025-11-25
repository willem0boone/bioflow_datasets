import shutil
from pathlib import Path

# -------------------------------------------------------
# Input paths (your original files)
# -------------------------------------------------------
gif_src = Path("../plots/map_combined.gif")
heatmap_src = Path("../plots/aggregated_heatmap_combined_dark.html")
sunburst_src = Path("../plots/sunburst/all_data.html")
video1_src = Path("../sources/DTO Animation - GENERAL.mp4")
video2_src = Path("../sources/DTO-Bioflow_Klaas_shortvideo_Final_Captions.mp4")

# -------------------------------------------------------
# Output structure
# ../dashboard/
#     dashboard.html
#     /sources/
# -------------------------------------------------------

dashboard_dir = Path("../dashboard")
sources_dir = dashboard_dir / "sources"
sources_dir.mkdir(parents=True, exist_ok=True)

# Copy files to sources/
gif_dst = sources_dir / gif_src.name
heatmap_dst = sources_dir / heatmap_src.name
sunburst_dst = sources_dir / sunburst_src.name
video1_dst = sources_dir / video1_src.name
video2_dst = sources_dir / video2_src.name

shutil.copy2(gif_src, gif_dst)
shutil.copy2(heatmap_src, heatmap_dst)
shutil.copy2(sunburst_src, sunburst_dst)
shutil.copy2(video1_src, video1_dst)
shutil.copy2(video2_src, video2_dst)

# Local paths inside dashboard
gif_rel = f"sources/{gif_dst.name}"
heatmap_rel = f"sources/{heatmap_dst.name}"
sunburst_rel = f"sources/{sunburst_dst.name}"
video1_rel = f"sources/{video1_dst.name}"
video2_rel = f"sources/{video2_dst.name}"

# -------------------------------------------------------
# Generate the dashboard HTML
# -------------------------------------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Combined Dashboard</title>
    <style>
        body {{
            margin: 0;
            height: 100vh;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
        }}
        .pane {{
            border: 1px solid #222;
            overflow: hidden;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        img, video {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: black;
        }}
    </style>
</head>

<body>

    <!-- Top Left: GIF -->
    <div class="pane">
        <img src="{gif_rel}" alt="GIF Pane">
    </div>

    <!-- Top Right: Alternating Local Videos -->
    <div class="pane">
        <video id="topVideo" autoplay muted controls></video>
        <script>
            const videos = ["{video1_rel}", "{video2_rel}"];
            let current = 0;
            const vid = document.getElementById("topVideo");
            vid.src = videos[current];
            vid.play();
            vid.onended = function() {{
                current = (current + 1) % videos.length;
                vid.src = videos[current];
                vid.play();
            }};
        </script>
    </div>

    <!-- Bottom Left: Heatmap HTML -->
    <div class="pane">
        <iframe src="{heatmap_rel}"></iframe>
    </div>

    <!-- Bottom Right: Sunburst HTML -->
    <div class="pane">
        <iframe src="{sunburst_rel}"></iframe>
    </div>

</body>
</html>
"""

# Write final dashboard file
output_file = dashboard_dir / "dashboard.html"
output_file.write_text(html, encoding="utf-8")

print("Dashboard created at:", output_file.resolve())
print("All original files copied to:", sources_dir.resolve())
