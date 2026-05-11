from flask import Blueprint, request, jsonify
from datetime import datetime
from services.groq_client import call_groq
from services.cache import get_from_cache, set_cache
from services.metrics import response_times
from services.utils import sanitize_input
import json
import time

describe_bp = Blueprint("describe", __name__)


def load_prompt(text):
    with open("prompts/describe.txt", "r") as f:
        return f.read().replace("{input}", text)


@describe_bp.route("/describe", methods=["POST"])
def describe():
    start = time.time()
    data = request.get_json()

    # 🔐 Validation
    if not data or "text" not in data:
        return jsonify({"error": "Missing text"}), 400

    raw_text = data["text"]

    if not isinstance(raw_text, str) or not raw_text.strip():
        return jsonify({"error": "Invalid input"}), 400

    if len(raw_text) > 500:
        return jsonify({"error": "Input too long"}), 400

    # 🔥 Sanitization (Day 8 improvement)
    text = sanitize_input(raw_text)

    cache_key = f"describe:{text}"
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
            "description": "AI service unavailable",
            "risk_level": "medium",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        })

    try:
        parsed = json.loads(ai_response)
    except:
        return jsonify({
            "description": "Invalid AI response",
            "risk_level": "medium",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        })

    result = {
        "description": parsed.get("description"),
        "risk_level": parsed.get("risk_level"),
        "generated_at": datetime.utcnow().isoformat()
    }

    set_cache(cache_key, result)
    response_times.append(time.time() - start)

    return jsonify(result)