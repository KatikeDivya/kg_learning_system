import networkx as nx
from cohere_utils import map_known_topics_to_nodes


def create_user_knowledge(graph, known_topics):
    nodes = list(graph.nodes())
    return map_known_topics_to_nodes(nodes, known_topics)


def recommend_next_topics(graph, user_knowledge):
    recommendations = []

    for node in graph.nodes():
        if user_knowledge.get(node, 0) == 0:
            prerequisites = list(graph.predecessors(node))

            if all(user_knowledge.get(pr, 0) == 1 for pr in prerequisites):
                recommendations.append(node)

    return recommendations


def generate_learning_path(graph, user_knowledge):
    ordered = list(nx.topological_sort(graph))
    return [t for t in ordered if user_knowledge.get(t, 0) == 0]