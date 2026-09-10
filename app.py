from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import tempfile

from cohere_utils import detect_domain, extract_topics, extract_syllabus_topics, explain_recommendation, detect_level
from dynamic_graph import generate_learning_graph
from graph_loader import build_graph
from recommender import create_user_knowledge, recommend_next_topics, generate_learning_path
from data_manager import add_query, get_all_queries, get_stats
from pdf_extractor import extract_text_from_pdf, extract_syllabus_summary
from career_recommender import recommend_career

load_dotenv()
app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/graph")
def graph_page():
    return render_template("graph.html")

@app.route("/career")
def career_page():
    return render_template("career.html")


# CAREER RECOMMENDATION
@app.route("/api/career-recommend", methods=["POST"])
def career_recommend():
    data = request.get_json()
    answers = {
        "interest":   data.get("interest", ""),
        "work_style": data.get("work_style", ""),
        "field":      data.get("field", ""),
        "level":      data.get("level", "")
    }

    result = recommend_career(answers)
    return jsonify(result)


# START LEARNING FROM CAREER — feeds directly into existing pipeline
@app.route("/api/career-start", methods=["POST"])
def career_start():
    data = request.get_json()
    domain = data.get("domain", "General Programming")
    raw_level = data.get("level", "advanced").lower()
    
    if "beginner" in raw_level:
        level = "beginner"
    elif "some experience" in raw_level or "intermediate" in raw_level:
        level = "intermediate"
    else:
        level = "advanced"

    graph_data = generate_learning_graph(domain, level=level)
    graph = build_graph(graph_data)
    user_knowledge = create_user_knowledge(graph, [])
    learning_path = generate_learning_path(graph, user_knowledge)
    recommendations = recommend_next_topics(graph, user_knowledge)

    add_query(
        user_input=f"[Career Path] {domain}",
        domain=domain,
        learning_path=learning_path,
        recommendations=recommendations,
        graph_data=graph_data
    )

    return jsonify({
        "domain": domain,
        "level": level,
        "known_topics": [],
        "learning_path": learning_path,
        "recommendations": recommendations,
        "graph": graph_data
    })


# PDF UPLOAD
@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        raw_text = extract_text_from_pdf(tmp_path)
        syllabus_text = extract_syllabus_summary(raw_text) if raw_text.strip() else f"Course: {file.filename}"

        domain = detect_domain(syllabus_text)
        level = detect_level(syllabus_text)
        known_topics = []
        syllabus_topics = extract_syllabus_topics(syllabus_text)

        graph_data = generate_learning_graph(domain, syllabus_topics, level=level)
        graph = build_graph(graph_data)
        user_knowledge = create_user_knowledge(graph, known_topics)
        learning_path = generate_learning_path(graph, user_knowledge)
        recommendations = recommend_next_topics(graph, user_knowledge)

        add_query(
            user_input=f"[PDF Upload] {file.filename}",
            domain=domain,
            learning_path=learning_path,
            recommendations=recommendations,
            graph_data=graph_data
        )

        return jsonify({
            "domain": domain,
            "level": level,
            "known_topics": known_topics,
            "learning_path": learning_path,
            "recommendations": recommendations,
            "graph": graph_data,
            "source": "pdf",
            "filename": file.filename,
            "syllabus_topics": syllabus_topics
        })
    except Exception as e:
        print(f"[Upload Error] {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


#  TEXT INPUT
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_input = data.get("text", "")

    domain = detect_domain(user_input)
    level = detect_level(user_input)
    known_topics = extract_topics(user_input)
    graph_data = generate_learning_graph(domain, level=level, user_input=user_input)
    graph = build_graph(graph_data)
    user_knowledge = create_user_knowledge(graph, known_topics)
    learning_path = generate_learning_path(graph, user_knowledge)
    recommendations = recommend_next_topics(graph, user_knowledge)

    add_query(
        user_input=user_input,
        domain=domain,
        learning_path=learning_path,
        recommendations=recommendations,
        graph_data=graph_data
    )

    return jsonify({
        "domain": domain,
        "level": level,
        "known_topics": known_topics,
        "learning_path": learning_path,
        "recommendations": recommendations,
        "graph": graph_data
    })


@app.route("/api/explain-topic", methods=["POST"])
def explain_topic():
    data = request.get_json() or {}
    topic = data.get("topic", "")
    domain = data.get("domain", "")
    level = data.get("level", "advanced")

    if not topic or not domain:
        return jsonify({"error": "Missing topic or domain"}), 400

    explanation = explain_recommendation(topic, domain, level=level)
    return jsonify({"topic": topic, "explanation": explanation})


@app.route("/api/stored-data", methods=["GET"])
def get_stored_data():
    queries = get_all_queries()
    return jsonify({"total_queries": len(queries), "queries": queries})

@app.route("/api/stats", methods=["GET"])
def get_data_stats():
    return jsonify(get_stats())

@app.route("/api/domain/<domain>", methods=["GET"])
def get_domain_info(domain):
    from data_manager import get_domain_data
    domain_data = get_domain_data(domain)
    if domain_data:
        return jsonify({"domain": domain, "data": domain_data})
    return jsonify({"error": "Domain not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)