import shutil
from pathlib import Path

# -------------------------------------------------------
# Input files
# -------------------------------------------------------

# TOP LEFT
heatmap_src = Path("../plots/aggregated_heatmap_combined_dark.html")

# TOP RIGHT: 2 alternating videos
videoA_src = Path("../sources/DTO-Bioflow_Klaas_shortvideo_Final_Captions.mp4")
videoB_src = Path("../sources/DOF_2025_DTO-BioFlow_booth.mp4")

# BOTTOM LEFT: two videos selectable with NEXT button
timeline_mp4_src = Path("../plots/timeline/source_all_combined_log.mp4")
map_mp4_src = Path("../plots/map_combined.mp4")

# BOTTOM RIGHT (horizontal split)
sunburst_call1_src = Path("../plots/sunburst/call1.html")
sensor_src = Path("../plots/sunburst/sensor.html")

# -------------------------------------------------------
# Output structure
# -------------------------------------------------------

dashboard_dir = Path("../dashboard")
sources_dir = dashboard_dir / "sources"
sources_dir.mkdir(parents=True, exist_ok=True)

# Files to copy
to_copy = [
    heatmap_src,
    videoA_src,
    videoB_src,
    timeline_mp4_src,
    map_mp4_src,
    sunburst_call1_src,
    sensor_src,
]

for src in to_copy:
    shutil.copy2(src, sources_dir / src.name)

# Local dashboard references
heatmap_rel = f"sources/{heatmap_src.name}"

videoA_rel = f"sources/{videoA_src.name}"
videoB_rel = f"sources/{videoB_src.name}"

timeline_rel = f"sources/{timeline_mp4_src.name}"
map_rel = f"sources/{map_mp4_src.name}"

sunburst_call1_rel = f"sources/{sunburst_call1_src.name}"
sensor_rel = f"sources/{sensor_src.name}"

# -------------------------------------------------------
# HTML dashboard generator
# -------------------------------------------------------

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DTO Dashboard</title>

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
            position: relative;
        }}

        .title {{
            position: absolute;
            top: 5px;
            left: 10px;
            z-index: 10;
            padding: 4px 8px;
            background: rgba(0,0,0,0.65);
            color: white;
            font-size: 16px;
            border-radius: 4px;
            font-family: Arial, sans-serif;
        }}

        .next-btn {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            z-index: 11;
            background: rgba(0,0,0,0.7);
            color: white;
            border: 1px solid #ccc;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        video {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: black;
        }}

        .split-horizontal {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            height: 100%;
        }}
    </style>
</head>

<body>

    <!-- TOP LEFT -->
    <div class="pane">
        <div class="title">Heatmap of DTO-Bioflow observations</div>
        <iframe src="{heatmap_rel}"></iframe>
    </div>

    <!-- TOP RIGHT: Alternating Videos -->
    <div class="pane">
        <video id="topRightVideo" autoplay muted controls></video>
        <script>
            const vidsTR = ["{videoA_rel}", "{videoB_rel}"];
            let idxTR = 0;
            const vTR = document.getElementById("topRightVideo");
            vTR.src = vidsTR[idxTR];
            vTR.play();
            vTR.onended = function() {{
                idxTR = (idxTR + 1) % vidsTR.length;
                vTR.src = vidsTR[idxTR];
                vTR.play();
            }};
        </script>
    </div>

    <!-- BOTTOM LEFT: Video with NEXT button -->
    <div class="pane">
        <div class="title">DTO-Bioflow Observations</div>
        <button class="next-btn" id="nextBL">Next ▶</button>

        <video id="bottomLeftVideo" autoplay muted loop controls></video>

        <script>
            const vidsBL = ["{timeline_rel}", "{map_rel}"];
            let idxBL = 0;

            const vBL = document.getElementById("bottomLeftVideo");
            const nextBtnBL = document.getElementById("nextBL");

            // Load first video
            vBL.src = vidsBL[idxBL];
            vBL.play();

            // On button click, switch videos
            nextBtnBL.onclick = function() {{
                idxBL = (idxBL + 1) % vidsBL.length;
                vBL.src = vidsBL[idxBL];
                vBL.play();
            }};
        </script>
    </div>

    <!-- BOTTOM RIGHT: Horizontal Split -->
    <div class="pane split-horizontal">

        <!-- Left side -->
        <div style="position: relative; border-right: 1px solid #222;">
            <div class="title">Taxonomic Diversity Observations</div>
            <iframe src="{sunburst_call1_rel}"></iframe>
        </div>

        <!-- Right side -->
        <div style="position: relative;">
            <div class="title">Taxonomic Diversity Sensor Observations</div>
            <iframe src="{sensor_rel}"></iframe>
        </div>

    </div>

</body>
</html>
"""

# Write dashboard file
output_file = dashboard_dir / "dashboard.html"
output_file.write_text(html, encoding="utf-8")

print("Dashboard created at:", output_file.resolve())
print("Sources copied to:", sources_dir.resolve())
