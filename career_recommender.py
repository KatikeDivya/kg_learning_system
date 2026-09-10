import cohere
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))


def _safe_chat(message, temperature=0.3, fallback="{}"):
    try:
        message = message.encode("ascii", errors="ignore").decode("ascii")[:2500]
        res = co.chat(model="command-a-03-2025", message=message, temperature=temperature)
        return res.text.strip()
    except Exception as e:
        print(f"[Career Recommender Error] {e}")
        return fallback


def recommend_career(answers: dict) -> dict:
    """
    Takes quiz answers and returns a career recommendation with domain.

    answers = {
        "interest":   "building apps / analyzing data / securing systems / etc.",
        "work_style": "creative / logical / research / hands-on",
        "field":      "web / mobile / AI / security / games / data / cloud / etc.",
        "level":      "beginner / some experience / intermediate"
    }
    """

    prompt = f"""You are a career guidance expert for post-graduate engineering/science students.

A student answered these questions:
- What excites them: {answers.get('interest', '')}
- How they like to work: {answers.get('work_style', '')}
- Field of interest: {answers.get('field', '')}
- Current level: {answers.get('level', '')}

Based on these answers, recommend the BEST highly advanced, specialized career path for this student.

Return ONLY this JSON (no extra text):
{{
  "career_title": "e.g. Distributed Systems Engineer",
  "why_it_fits": "2-3 sentences explaining why this advanced career suits their interests and M.Tech level expertise",
  "domain": "e.g. Distributed Systems",
  "top_skills": ["Advanced Skill 1", "Advanced Skill 2", "Advanced Skill 3", "Advanced Skill 4", "Advanced Skill 5"],
  "salary_range": "e.g. $100,000 - $180,000",
  "difficulty": "Challenging / Highly Specialized",
  "job_roles": ["Role 1", "Role 2", "Role 3"],
  "also_consider": [
    {{"career_title": "Alternative Advanced Career", "domain": "Domain Name"}},
    {{"career_title": "Alternative Advanced Career 2", "domain": "Domain Name 2"}}
  ]
}}"""

    raw = _safe_chat(prompt, temperature=0.3)

    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return {
        "career_title": "Senior Research Engineer",
        "why_it_fits": "A highly specialized role that matches advanced research interests and technical expertise at the post-graduate level.",
        "domain": "Advanced Engineering",
        "top_skills": ["Advanced Algorithms", "System Architecture Design", "Distributed Computing", "Research Methodologies", "Mathematical Modeling"],
        "salary_range": "$110,000 - $190,000",
        "difficulty": "Challenging",
        "job_roles": ["Research Scientist", "Distributed Systems Engineer", "Principal Architect"],
        "also_consider": [
            {"career_title": "Machine Learning Architect", "domain": "Machine Learning Theory"},
            {"career_title": "Cloud Solutions Principal", "domain": "Cloud Infrastructure Systems"}
        ]
    }
