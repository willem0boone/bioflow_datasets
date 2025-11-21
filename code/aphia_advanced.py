import pandas as pd
import plotly.express as px
import json


def fill_nulls(path):
    filled = []
    last = None
    for val in path:
        if val is not None:
            filled.append(val)
            last = val
        else:
            filled.append(last)
    print(f"[fill_nulls] {path} -> {filled}")
    return filled


def collapse_consecutive(path):
    if not path:
        return path
    collapsed = [path[0]]
    for v in path[1:-1]:
        if v != collapsed[-1]:
            collapsed.append(v)
    collapsed.append(path[-1])
    print(f"[collapse_consecutive] {path} -> {collapsed}")
    return collapsed


def build_sunburst_df(taxonomy_data):
    rows = []
    for idx, record in enumerate(taxonomy_data):
        path = [val if val is not None else "Unknown" for val in
                record["taxonomy"]]
        path = collapse_consecutive(path)
        count = record.get("count", 0)

        for i, name in enumerate(path):
            parent = "" if i == 0 else path[i - 1]
            value = count if i == len(path) - 1 else 0
            node_id = "|".join(path[:i + 1])
            rows.append({"id": node_id, "label": name, "parent": parent,
                         "value": value})
            print(
                f"[row] id={node_id}, label={name}, parent={parent}, value={value}")

    df = pd.DataFrame(rows)
    print(f"[build_sunburst_df] initial rows: {len(df)}")
    df = df[df["id"] != df["parent"]]  # remove self-parenting
    df = df.groupby(["id", "label", "parent"], as_index=False)["value"].sum()
    print(f"[build_sunburst_df] after grouping duplicates: {len(df)} rows")
    return df


def remove_zero_branches(df):
    leaves = df[df["value"] > 0]
    print(f"[remove_zero_branches] leaf nodes count: {len(leaves)}")
    valid_ids = set()
    for leaf_id in leaves["id"]:
        parts = leaf_id.split("|")
        for i in range(1, len(parts) + 1):
            valid_ids.add("|".join(parts[:i]))
    df_filtered = df[df["id"].isin(valid_ids)].reset_index(drop=True)
    print(
        f"[remove_zero_branches] after removing zero branches: {len(df_filtered)} rows")
    return df_filtered


def add_missing_parents(df):
    all_ids = set(df['id'])
    all_parents = set(df['parent']) - {""}
    missing_parents = all_parents - all_ids
    print(
        f"[add_missing_parents] Adding {len(missing_parents)} missing parents")

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


if __name__ == "__main__":
    # Load your taxonomy data
    with open("taxonomy_data.json", "r") as f:
        taxonomy_data = json.load(f)

    print(f"[main] Total taxonomy records: {len(taxonomy_data)}")

    # Build sunburst DataFrame
    df_sb = build_sunburst_df(taxonomy_data)
    df_sb = remove_zero_branches(df_sb)
    df_sb = add_missing_parents(df_sb)

    # Diagnostics
    print(f"[main] Final DataFrame ready for plotting: {len(df_sb)} rows")
    print(df_sb.head(20))
    print(f"Unique IDs: {df_sb['id'].nunique()}")
    print(f"Unique labels: {df_sb['label'].nunique()}")
    print(f"Unique parents: {df_sb['parent'].nunique()}")
    print(f"Total value sum: {df_sb['value'].sum()}")

    missing_parents = set(df_sb['parent']) - set(df_sb['id']) - {""}
    print(f"Missing parents (should be empty): {missing_parents}")

    # Plot sunburst
    fig = px.sunburst(df_sb, ids='id', names='label', parents='parent',
                      values='value')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    fig.write_html("sunburst_plot_no.html")
    print("[main] Plot saved as sunburst_plot.html, open it in a browser.")
