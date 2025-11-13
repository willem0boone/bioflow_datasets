import pandas as pd
import networkx as nx
from pyvis.network import Network

# --------------------------
# Dataset
# --------------------------
data = [
    ["A", "A2", "A21", "A211", 20],
    ["A", "A2", "A21", "A212", 30],
    ["A", "A3", "A31", "A311", 25],
    ["A", "A3", "A32", "A321", 25],
    ["A", "A3", "A32", "A322", 25],
    ["A", "A3", "A32", "A323", 25],
    ["A", "A4", "A41", "A411", 25],
    ["A", "A4", "A41", "A412", 25],
    ["A", "A4", "A42", "A421", 50],
]

df = pd.DataFrame(data, columns=["kingdom", "phylum", "class", "order", "count"])

# --------------------------
# Build a directed graph
# --------------------------
G = nx.DiGraph()

# Add edges and nodes
for _, row in df.iterrows():
    path = [row["kingdom"], row["phylum"], row["class"], row["order"]]
    count = row["count"]
    # Connect nodes in the path
    for parent, child in zip(path[:-1], path[1:]):
        G.add_edge(parent, child)
        # Store/update counts on nodes (sum of counts for duplicates)
        if "count" in G.nodes[parent]:
            G.nodes[parent]["count"] += count
        else:
            G.nodes[parent]["count"] = count
    # Add leaf node count
    if "count" in G.nodes[path[-1]]:
        G.nodes[path[-1]]["count"] += count
    else:
        G.nodes[path[-1]]["count"] = count

# --------------------------
# Create PyVis network
# --------------------------
net = Network(height="800px", width="1000px", directed=True)

# Add nodes with size proportional to count
for node, attr in G.nodes(data=True):
    net.add_node(node, label=node, title=f"{node}: {attr['count']}",
                 size=5 + attr["count"] / 2,  # scale size
                 color=None)  # color can be set if desired

# Add edges
for source, target in G.edges():
    net.add_edge(source, target)

# --------------------------
# Save and show interactive HTML
# --------------------------
net.show("network_tree.html", notebook=False)
print("✅ Saved 'network_tree.html' — open in browser to view the interactive network.")
