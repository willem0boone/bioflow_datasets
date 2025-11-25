import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from collections import defaultdict

# Input folders
folders = {
    Path("../data/worms/worms_call1_data"): "call1",
    Path("../data/worms/worms_sensor_data"): "sensor",
}

output_base_dir = Path("../plots/sunburst")
output_base_dir.mkdir(parents=True, exist_ok=True)


def build_sunburst_df(taxonomy_data):
    rows = []
    for record in taxonomy_data:
        path = [val if val is not None else "Unknown" for val in
                record["taxonomy"]]
        while len(path) < 7:
            path.append("Unknown")
        count = record.get("count", 0)
        for i, name in enumerate(path):
            node_id = "|".join(path[:i + 1])
            parent = "" if i == 0 else "|".join(path[:i])
            value = count if i == len(path) - 1 else 0
            rows.append({"id": node_id, "label": name, "parent": parent,
                         "value": value})
    df = pd.DataFrame(rows)
    df = df.groupby(["id", "label", "parent"], as_index=False)["value"].sum()
    return df


def remove_zero_branches(df):
    leaves = df[df["value"] > 0]
    valid_ids = set()
    for leaf_id in leaves["id"]:
        parts = leaf_id.split("|")
        for i in range(1, len(parts) + 1):
            valid_ids.add("|".join(parts[:i]))
    return df[df["id"].isin(valid_ids)].reset_index(drop=True)


def add_missing_parents(df):
    all_ids = set(df['id'])
    all_parents = set(df['parent']) - {""}
    missing_parents = all_parents - all_ids
    rows = []
    for parent in missing_parents:
        parts = parent.split("|")
        label = parts[-1]
        parent_id = "" if len(parts) == 1 else "|".join(parts[:-1])
        rows.append(
            {"id": parent, "label": label, "parent": parent_id, "value": 0})
    if rows:
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    return df


def merge_taxonomies(all_taxonomies):
    merged = defaultdict(int)
    for record in all_taxonomies:
        key = tuple(val if val is not None else "Unknown" for val in
                    record["taxonomy"])
        merged[key] += record.get("count", 0)
    return [{"taxonomy": list(k), "count": v} for k, v in merged.items()]


if __name__ == "__main__":
    all_data_combined = []

    for input_dir, name in folders.items():
        output_dir = output_base_dir / name
        output_dir.mkdir(parents=True, exist_ok=True)
        folder_data = []

        # Process each JSON file
        for json_file in input_dir.glob("*.json"):
            with open(json_file, "r") as f:
                taxonomy_data = json.load(f)
                folder_data.extend(taxonomy_data)

            # Individual sunburst
            df_sb = build_sunburst_df(taxonomy_data)
            df_sb = remove_zero_branches(df_sb)
            df_sb = add_missing_parents(df_sb)
            fig = px.sunburst(df_sb, ids='id', names='label', parents='parent',
                              values='value')
            fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            output_file = output_dir / f"{json_file.stem}.html"
            fig.write_html(output_file)
            print(f"Saved individual sunburst: {output_file}")

        # Merge all JSONs in the folder
        merged_data = merge_taxonomies(folder_data)
        df_sb = build_sunburst_df(merged_data)
        df_sb = remove_zero_branches(df_sb)
        df_sb = add_missing_parents(df_sb)
        fig = px.sunburst(df_sb, ids='id', names='label', parents='parent',
                          values='value')
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        merged_file = output_base_dir / f"{name}.html"  # call1.html or sensor.html
        fig.write_html(merged_file)
        print(f"Saved merged sunburst for {name}: {merged_file}")

        all_data_combined.extend(folder_data)

    # Merge all data together
    merged_all = merge_taxonomies(all_data_combined)
    df_sb = build_sunburst_df(merged_all)
    df_sb = remove_zero_branches(df_sb)
    df_sb = add_missing_parents(df_sb)
    fig = px.sunburst(df_sb, ids='id', names='label', parents='parent',
                      values='value')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    combined_file = output_base_dir / "all_data.html"
    fig.write_html(combined_file)
    print(f"Saved merged sunburst for all data: {combined_file}")



