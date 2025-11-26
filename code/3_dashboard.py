import shutil
from pathlib import Path

# -------------------------------------------------------
# Input paths (your original files + new files)
# -------------------------------------------------------
gif_src = Path("../plots/map_combined.gif")
timeline_gif_src = Path("../plots/timeline/source_all_combined_log.gif")  # New GIF
heatmap_src = Path("../plots/aggregated_heatmap_combined_dark.html")
sunburst_src = Path("../plots/sunburst/all_data.html")
video1_src = Path("../sources/DTO Animation - GENERAL.mp4")
video2_src = Path("../sources/DTO-Bioflow_Klaas_shortvideo_Final_Captions.mp4")
new_video_src = video1_src  # Mock the new video with the same one

# -------------------------------------------------------
# Output structure
# -------------------------------------------------------
dashboard_dir = Path("../dashboard")
sources_dir = dashboard_dir / "sources"
sources_dir.mkdir(parents=True, exist_ok=True)

# Copy files to sources/
for src in [gif_src, timeline_gif_src, heatmap_src, sunburst_src, video1_src, video2_src]:
    dst = sources_dir / src.name
    shutil.copy2(src, dst)

# Local paths inside dashboard
gif_rel = f"sources/{gif_src.name}"
timeline_gif_rel = f"sources/{timeline_gif_src.name}"
heatmap_rel = f"sources/{heatmap_src.name}"
sunburst_rel = f"sources/{sunburst_src.name}"
video1_rel = f"sources/{video1_src.name}"
video2_rel = f"sources/{video2_src.name}"
new_video_rel = f"sources/{new_video_src.name}"  # Mock video

# -------------------------------------------------------
# Generate the dashboard HTML (2 rows x 3 columns)
# -------------------------------------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Extended Dashboard</title>
    <style>
        body {{
            margin: 0;
            height: 100vh;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
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

    <!-- Top Middle: Alternating Local Videos -->
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

    <!-- Top Right: New Video (mocked) -->
    <div class="pane">
        <video autoplay muted controls>
            <source src="{new_video_rel}" type="video/mp4">
        </video>
    </div>

    <!-- Bottom Left: Heatmap HTML -->
    <div class="pane">
        <iframe src="{heatmap_rel}"></iframe>
    </div>

    <!-- Bottom Middle: Sunburst HTML -->
    <div class="pane">
        <iframe src="{sunburst_rel}"></iframe>
    </div>

    <!-- Bottom Right: New GIF -->
    <div class="pane">
        <img src="{timeline_gif_rel}" alt="Timeline GIF">
    </div>

</body>
</html>
"""

# Write final dashboard file
output_file = dashboard_dir / "dashboard.html"
output_file.write_text(html, encoding="utf-8")

print("Dashboard created at:", output_file.resolve())
print("All original files copied to:", sources_dir.resolve())
