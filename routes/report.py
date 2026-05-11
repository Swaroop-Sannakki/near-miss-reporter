from flask import Blueprint, request, jsonify
from datetime import datetime
from services.groq_client import call_groq
from services.cache import get_from_cache, set_cache
from services.metrics import response_times
from services.utils import sanitize_input
import json
import time

report_bp = Blueprint("report", __name__)


def load_prompt(text):
    with open("prompts/report.txt", "r") as f:
        return f.read().replace("{input}", text)


@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    start = time.time()
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing text"}), 400

    raw_text = data["text"]

    if not isinstance(raw_text, str) or not raw_text.strip():
        return jsonify({"error": "Invalid input"}), 400

    if len(raw_text) > 500:
        return jsonify({"error": "Input too long"}), 400

    text = sanitize_input(raw_text)

    cache_key = f"report:{text}"
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify(cached)

    prompt = load_prompt(text)

    try:
        ai_response = call_groq(prompt)
    except:
        ai_response = None

    if not ai_response:
        return jsonify({
            "title": "AI unavailable",
            "summary": "",
            "overview": "",
            "key_items": [],
            "recommendations": [],
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        })

    try:
        parsed = json.loads(ai_response)
    except:
        return jsonify({
            "title": "Invalid AI response",
            "summary": "",
            "overview": "",
            "key_items": [],
            "recommendations": [],
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        })

    result = {
        "title": parsed.get("title"),
        "summary": parsed.get("summary"),
        "overview": parsed.get("overview"),
        "key_items": parsed.get("key_items"),
        "recommendations": parsed.get("recommendations"),
        "generated_at": datetime.utcnow().isoformat()
    }

    set_cache(cache_key, result)
    response_times.append(time.time() - start)

    return jsonify(result)