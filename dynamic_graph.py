import cohere
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))


import networkx as nx

def clean_json_string(json_str):
    """Clean common LLM JSON syntax errors like trailing commas in arrays/objects."""
    json_str = re.sub(r',\s*\]', ']', json_str)
    json_str = re.sub(r',\s*\}', '}', json_str)
    return json_str


def normalize_string(s):
    """Lowercase and strip all non-alphanumeric characters for robust case-insensitive matching."""
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def generate_learning_graph(domain, syllabus_topics=None, level=None, user_input=None):
    syllabus_hint = ""
    level_str = (level or "advanced").lower()
    
    if syllabus_topics and len(syllabus_topics) > 0:
        syllabus_hint = f"""
- The user has uploaded a syllabus containing these topics: {', '.join(syllabus_topics[:25])}
- Design a comprehensive, realistic learning path of 20-25 topics that covers this syllabus.
- Crucially, follow these structure rules:
  1. At least 6-8 topics MUST be foundational prerequisites (such as base programming languages, mathematics, command-line tools, or basic concepts) that are required to understand the syllabus, even if they are not explicitly written in the syllabus.
  2. The remaining topics should group, summarize, and synthesize the syllabus topics. Do NOT list the syllabus topics verbatim as node names, and do NOT structure them as a simple linear chain.
  3. Ensure the graph starts with the foundational nodes and branches out logically to the specialized syllabus topics.
"""

    # Customize instructions based on experience level
    if "beginner" in level_str:
        level_instruction = """- Topics should focus on fundamental prerequisites, basic syntax, introductory theory, step-by-step guides, and foundational coding/concepts."""
    elif "intermediate" in level_str:
        level_instruction = """- Topics should assume basic knowledge of the domain and focus on intermediate application architecture, standard libraries, API usage, algorithms, and practical implementation patterns."""
    else:
        level_instruction = """- Skip basic, introductory, or trivial topics (e.g., do NOT include basic syntax or introductory tutorials).
- Focus on advanced theoretical foundations, mathematical modeling, research-level concepts, state-of-the-art architectures, performance optimization, and complex system design."""

    user_context_hint = ""
    if user_input:
        user_context_hint = f"\nThe student has the following background or learning goals: {user_input}\nTailor the choice of topics to align with these specific interests or gaps.\n"

    prompt = f"""Create a highly customized learning path for: {domain}
{syllabus_hint}{user_context_hint}
Requirements:
{level_instruction}
- Generate exactly 20-25 topics covering the full learning journey.
- EACH TOPIC NAME must be a complete, natural technical concept (maximum 8 words). Do not cut off mid-sentence.
- Define a Directed Acyclic Graph (DAG) of prerequisites (edges) between these topics. Show realistic academic prerequisites.
- Avoid circular dependencies.
- Output only JSON

Format:
{{
  "topics": ["Topic A", "Topic B", "Topic C", "Topic D"],
  "edges": [
    ["Topic A", "Topic B"],
    ["Topic A", "Topic C"],
    ["Topic B", "Topic D"],
    ["Topic C", "Topic D"]
  ]
}}

Learning path:"""

    try:
        text = co.chat(
            model="command-a-03-2025",
            message=prompt.encode("ascii", errors="ignore").decode("ascii"),
            temperature=0.3
        ).text.strip()
    except Exception as e:
        print(f"[Graph Error] {e}")
        return _fallback_graph(domain, syllabus_topics, level_str)

    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            cleaned_json = clean_json_string(match.group())
            data = json.loads(cleaned_json)
            raw_topics = data.get("topics", [])

            # Clean and map topics (allow natural length, clean numbers/unit markers)
            cleaned_topics = []
            topic_mapping = {}
            for t in raw_topics:
                cleaned = str(t).strip()
                cleaned = re.sub(r'^(?:unit\s+\d+[:\-]?|module\s+\d+[:\-]?|\d+\.\s*)\s*', '', cleaned, flags=re.IGNORECASE)
                if cleaned:
                    cleaned_topics.append(cleaned)
                    topic_mapping[t] = cleaned

            # Deduplicate while preserving order
            seen = set()
            topics = []
            normalized_topics = {} # maps normalized_name -> actual_clean_name
            for t in cleaned_topics:
                if t not in seen:
                    topics.append(t)
                    seen.add(t)
                    normalized_topics[normalize_string(t)] = t

            if len(topics) < 15:
                # Add fallback topics to reach minimum length
                while len(topics) < 20:
                    new_topic = f"Related Topic {len(topics) + 1}"
                    topics.append(new_topic)
                    seen.add(new_topic)
                    normalized_topics[normalize_string(new_topic)] = new_topic
            elif len(topics) > 25:
                topics = topics[:25]
                seen = set(topics)
                normalized_topics = {normalize_string(t): t for t in topics}

            # Map and validate edges case-insensitively using normalized_topics
            raw_edges = data.get("edges", [])
            edges = []
            for e in raw_edges:
                if isinstance(e, list) and len(e) == 2:
                    src, dst = e[0], e[1]
                    clean_src = topic_mapping.get(src, re.sub(r'^(?:unit\s+\d+[:\-]?|module\s+\d+[:\-]?|\d+\.\s*)\s*', '', str(src).strip(), flags=re.IGNORECASE))
                    clean_dst = topic_mapping.get(dst, re.sub(r'^(?:unit\s+\d+[:\-]?|module\s+\d+[:\-]?|\d+\.\s*)\s*', '', str(dst).strip(), flags=re.IGNORECASE))
                    
                    norm_src = normalize_string(clean_src)
                    norm_dst = normalize_string(clean_dst)
                    
                    match_src = normalized_topics.get(norm_src)
                    match_dst = normalized_topics.get(norm_dst)
                    
                    if match_src and match_dst and match_src != match_dst:
                        edges.append([match_src, match_dst])

            # Build graph and break cycles using NetworkX
            g = nx.DiGraph()
            g.add_nodes_from(topics)
            g.add_edges_from(edges)

            while not nx.is_directed_acyclic_graph(g):
                try:
                    cycle = nx.find_cycle(g)
                    if cycle:
                        u, v = cycle[0][0], cycle[0][1]
                        g.remove_edge(u, v)
                        print(f"[Cycle Detector] Removed cycle edge: {u} -> {v}")
                except nx.NetworkXNoCycle:
                    break

            cleaned_edges = [list(edge) for edge in g.edges()]

            # If no valid edges, build a basic topological flow (linear fallback)
            if not cleaned_edges and len(topics) > 1:
                cleaned_edges = [[topics[i], topics[i + 1]] for i in range(len(topics) - 1)]

            return {"topics": topics, "edges": cleaned_edges}
        except Exception as e:
            print(f"[Parsing Error] {e}")
            pass

    return _fallback_graph(domain, syllabus_topics, level_str)


def _fallback_graph(domain, syllabus_topics=None, level=None):
    if syllabus_topics:
        try:
            print("[Fallback] Syllabus-based graph generation failed. Retrying with a standard domain prompt...")
            # Retry standard generation without syllabus topics to get a realistic path
            std_graph = generate_learning_graph(domain, syllabus_topics=None, level=level)
            if std_graph and len(std_graph.get("topics", [])) >= 5:
                return std_graph
        except Exception as e:
            print(f"[Fallback Error] Standard retry failed: {e}")
            pass

        # If that fails, clean syllabus topics without truncating to 4 words
        topics = [re.sub(r'^(?:unit\s+\d+[:\-]?|module\s+\d+[:\-]?|\d+\.\s*)\s*', '', str(t).strip(), flags=re.IGNORECASE) for t in syllabus_topics[:25]]
        topics = [t for t in topics if t]
        if len(topics) >= 3:
            edges = [[topics[i], topics[i + 1]] for i in range(len(topics) - 1)]
            return {"topics": topics, "edges": edges}

    topics = [
        f"{domain} Foundations",
        "Core Concepts & Syntax",
        "Intermediate Architecture",
        "Advanced System Design",
        "Practical Projects & Deployment"
    ]
    edges = [[topics[i], topics[i + 1]] for i in range(len(topics) - 1)]
    return {"topics": topics, "edges": edges}