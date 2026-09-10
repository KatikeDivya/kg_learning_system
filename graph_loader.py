import networkx as nx


def build_graph(data):
    G = nx.DiGraph()

    for t in data["topics"]:
        G.add_node(t)

    for src, dst in data["edges"]:
        # Add edge and check if it introduces a cycle
        G.add_edge(src, dst)
        if not nx.is_directed_acyclic_graph(G):
            # Remove the edge immediately to preserve DAG status
            G.remove_edge(src, dst)

    return G