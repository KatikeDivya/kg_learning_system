import cohere
import os
import re
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def _safe_chat(message, temperature=0.1, fallback=""):
    """Cohere chat with sanitization and error handling."""
    try:
        message = message.encode("ascii", errors="ignore").decode("ascii")
        message = message[:2500]
        res = co.chat(
            model="command-a-03-2025",
            message=message,
            temperature=temperature
        )
        return res.text.strip()
    except Exception as e:
        print(f"[Cohere Error] {e}")
        return fallback


# ---------------- DOMAIN DETECTION ----------------
def detect_domain(user_input):
    prompt = f"""Read the text below and return ONLY the main technical learning domain (2-5 words).

TEXT:
{user_input[:1500]}

Return only the domain name. Examples: Java Programming, Python Programming, Web Development, Machine Learning, Data Structures, Object Oriented Programming using Java.
Never return a sentence. Always return a short domain name.

Domain:"""

    raw = _safe_chat(prompt, temperature=0.1, fallback="General Programming")

    if len(raw.split()) > 6:
        keywords = [
            "Java", "Python", "Machine Learning", "Web Development",
            "Data Science", "Database", "Networks", "Android", "Cloud",
            "C++", "C#", ".NET", "React", "DevOps", "Cybersecurity",
            "Data Structures", "Operating Systems", "Software Engineering",
            "Object Oriented"
        ]
        for kw in keywords:
            if kw.lower() in raw.lower():
                return kw
        return " ".join(raw.split()[:4])

    return raw


# ---------------- TOPIC EXTRACTION (text input only) ----------------
def extract_topics(user_input):
    """
    For plain text input: extract what the user already knows.
    Returns empty list for PDF/syllabus content.
    """
    prompt = f"""The user wrote this text about what they already know or want to learn.
Extract ONLY the topics the user explicitly says they already know.

TEXT:
{user_input[:1000]}

Rules:
- Only include topics the user says they KNOW or HAVE LEARNED
- Do NOT include topics they want to learn
- If this looks like a syllabus or course description, return empty
- Comma-separated list only, no explanations
- If nothing found, return empty string

Known topics:"""

    raw = _safe_chat(prompt, temperature=0.1, fallback="")

    junk_phrases = ["no topics", "no text", "the text", "there is", "i cannot",
                    "not explicitly", "no explicit", "none", "empty", "syllabus"]
    if not raw or any(p in raw.lower() for p in junk_phrases):
        return []

    return [t.strip() for t in raw.split(",") if t.strip() and len(t.strip()) > 2]


# ---------------- SYLLABUS TOPIC EXTRACTION (PDF input) ----------------
def extract_syllabus_topics(syllabus_text):
    """
    Dynamically extract all topics from any syllabus/course PDF using Cohere.
    Works for any domain — Java, Python, Data Science, Networks, anything.
    """
    prompt = f"""You are reading a course syllabus. Extract every technical topic, concept, and subject taught in this course.

SYLLABUS:
{syllabus_text[:1500]}

Rules:
- Extract ALL topics regardless of domain or subject
- Return comma-separated list ONLY, no explanations, no numbering
- Be comprehensive — include every concept, technology, and subject mentioned
- Do not say "no topics" — always extract what is present

Topics covered:"""

    raw = _safe_chat(prompt, temperature=0.1, fallback="")

    # If Cohere fails or returns garbage, do a simple line-based extraction
    if not raw or len(raw) > 1000 or any(p in raw.lower() for p in ["no topics", "i cannot", "the text"]):
        return _line_based_extract(syllabus_text)

    topics = [t.strip() for t in raw.split(",") if t.strip() and len(t.strip()) > 2]
    return topics if topics else _line_based_extract(syllabus_text)


def _line_based_extract(text):
    """
    Generic fallback: extract topic-like lines from any syllabus.
    Looks for lines that start with known heading patterns (UNIT, topic names).
    Works for any subject — no hardcoded keywords.
    """
    topics = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        # Skip short, empty, or junk lines
        if len(line) < 5 or len(line) > 80:
            continue
        # Skip lines that are clearly not topics
        if re.match(r'^(for the|academic|course code|prerequisite|text book|reference|department|college|university|\d+$)', line, re.IGNORECASE):
            continue
        # Keep lines that look like topic headings (start with capital, no special chars)
        if re.match(r'^[A-Z][a-zA-Z\s\(\)/&,\-\.]+$', line) and len(line.split()) <= 8:
            topics.append(line)

    # Deduplicate while preserving order
    seen = set()
    result = []
    for t in topics:
        if t.lower() not in seen:
            result.append(t)
            seen.add(t.lower())

    return result[:25]


# ---------------- ROADMAP GENERATION ----------------
def generate_roadmap(domain):
    prompt = f"""Create a detailed, highly advanced, engineering level learning roadmap for: {domain}

Requirements:

- Skip basic introductory topics. Focus on advanced theoretical foundations, mathematical formulation, distributed architectures, performance optimization, and research-level methodologies.
- Output ONLY this JSON:
{{
  "phases": [
    {{
      "title": "Phase Name",
      "goal": "Advanced learning outcome / research objective",
      "topics": ["Advanced Topic - detailed theoretical and practical explanation", "Advanced Topic - detailed theoretical and practical explanation"]
    }}
  ]
}}"""

    return _safe_chat(prompt, temperature=0.4, fallback="{}")


# ---------------- RECOMMENDATION EXPLANATION ----------------
def explain_recommendation(topic, domain, level=None):
    level_str = (level or "advanced").lower()
    if "beginner" in level_str:
        prompt = f"""Explain the topic "{topic}" in the context of {domain} to a complete beginner.
Give 3-5 lines explaining what it is in simple terms, why it matters, and how it is used in practice, without using overly complex jargon."""
    elif "intermediate" in level_str:
        prompt = f"""Explain the topic "{topic}" in the context of {domain} to an intermediate student.
Give 3-5 lines focusing on its practical applications, standard libraries/frameworks, and common patterns or implementation considerations."""
    else:
        prompt = f"""Explain why the advanced level topic "{topic}" is crucial in {domain}.
Give 3-5 lines focusing on its advanced theoretical significance, mathematical foundations, or complex engineering and optimization challenges it addresses in research and industry."""
    
    return _safe_chat(prompt, temperature=0.3, fallback="Important foundational topic.")


# ---------------- SEMANTIC PRIOR KNOWLEDGE MAPPING ----------------
def map_known_topics_to_nodes(graph_nodes, known_topics):
    """
    Uses Cohere to semantically map user's known topics to the graph's nodes.
    Returns a dictionary of {node: 1 or 0}.
    """
    import json
    mapping = {node: 0 for node in graph_nodes}
    if not known_topics or not graph_nodes:
        return mapping

    # Clean known_topics
    clean_known = [t.strip() for t in known_topics if t.strip()]
    if not clean_known:
        return mapping

    prompt = f"""You are a career guidance expert for engineering/science students.
The learning path has these exact topics:
{json.dumps(graph_nodes)}

The student already knows or has completed these concepts/skills:
{json.dumps(clean_known)}

Determine which of the learning path topics the student ALREADY knows or has mastered based on their known concepts.
Rules:
- Mark a topic as known (1) if their known concepts clearly cover, include, or imply mastery of that topic.
- Be conservative: if it's not clear or they only know a small part of it, mark it as not known (0).
- Output ONLY a JSON object mapping each learning path topic to 1 or 0. Do not write any other text.

Example output:
{{
  "Topic A": 1,
  "Topic B": 0
}}

JSON Mapping:"""

    raw = _safe_chat(prompt, temperature=0.1, fallback="")
    
    # Try to parse JSON from response
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            llm_mapping = json.loads(match.group())
            # Validate mapping keys match graph_nodes
            for node in graph_nodes:
                # Direct match or case-insensitive match
                for k, v in llm_mapping.items():
                    if k.lower().strip() == node.lower().strip():
                        if v in [1, "1", True]:
                            mapping[node] = 1
                            break
            return mapping
        except Exception as e:
            print(f"[Semantic Mapping Parse Error] {e}")
            pass

    # Fallback to substring matching and basic token overlap if LLM fails
    print("[Semantic Mapping Fallback] Running local matching algorithms...")
    for topic in clean_known:
        topic_lower = topic.lower().strip()
        for node in graph_nodes:
            node_lower = node.lower().strip()
            # 1. Direct Substring
            if topic_lower in node_lower or node_lower in topic_lower:
                mapping[node] = 1
            # 2. Token overlap
            else:
                topic_words = set(topic_lower.split())
                node_words = set(node_lower.split())
                # Filter out small stop words
                stopwords = {"and", "or", "the", "a", "of", "in", "to", "for", "with", "using", "basics", "intro", "introduction"}
                topic_words = topic_words - stopwords
                node_words = node_words - stopwords
                if topic_words and node_words and len(topic_words & node_words) >= min(len(topic_words), len(node_words), 2):
                    mapping[node] = 1

    return mapping


# ---------------- EXPERIENCE LEVEL AUTO-DETECTION ----------------
def detect_level(user_input):
    """
    Detect the user's experience level (beginner, intermediate, advanced)
    based on their text query or course description/syllabus.
    """
    if not user_input or len(user_input.strip()) < 5:
        return "advanced"  # Default to advanced

    # Simple keyword heuristical preprocessing for efficiency
    text_lower = user_input.lower()
    
    # If they explicitly declare level, respect it
    if "complete beginner" in text_lower or "beginner" in text_lower or "from scratch" in text_lower or "no experience" in text_lower:
        return "beginner"
    if "advanced theory" in text_lower:
        return "advanced"

    prompt = f"""Read the text below and classify the user's technical experience level or the course complexity.
Technical levels:
- beginner: If they mention they are starting out, want the basics, have no experience, or if the text describes a fundamental/introductory course.
- intermediate: If they mention they have some programming experience, know the basics, want to learn a framework/library, or if the text describes a standard application development course.
- advanced: If they mention they are advanced, want advanced optimization, or if the text describes mathematical modeling, or complex system design.

TEXT:
{user_input[:1500]}

Return ONLY one word: beginner, intermediate, or advanced.
Level:"""

    raw = _safe_chat(prompt, temperature=0.1, fallback="advanced")
    raw_lower = raw.lower().strip()
    if "beginner" in raw_lower:
        return "beginner"
    if "intermediate" in raw_lower:
        return "intermediate"
    return "advanced"

# ---------------- RESEARCH ARTICLE SUMMARIZATION ----------------
def summarize_text(text: str, max_tokens: int = 600) -> str:
    """Summarize a research article or journal text into detailed bullet points.
    Returns a concise summary (≈250‑300 words) formatted as bullet points.
    """
    prompt = f"""
Summarize the following research article in detailed bullet points (3‑6 bullets). Include the core findings, methodology, and implications. Keep the total length under 300 words.

ARTICLE:
{text[:2000]}

Summary:"""
    return _safe_chat(prompt, temperature=0.3, fallback="Summary not available.")