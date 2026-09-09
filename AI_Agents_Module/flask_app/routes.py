import os
import requests
import urllib3
from flask import Blueprint, jsonify, request, render_template
from flask_app.agents.orchestrator import AgentOrchestrator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

agents_bp = Blueprint("agents", __name__)
orchestrator = AgentOrchestrator()

KOBO_TOKEN = os.getenv("KOBO_API_TOKEN")
FORM_ID = os.getenv("KOBO_FORM_ID")

def fetch_displaced_families_data():
    headers = {
        "Authorization": f"Token {KOBO_TOKEN}",
        "User-Agent": "Mozilla/5.0",
    }
    url = f"https://eu.kobotoolbox.org/api/v2/assets/{FORM_ID}/data.json?limit=1000"

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
        print(f"⚠️ Fetch Error: {e}")

    return []

@agents_bp.route("/", methods=["GET"])
def render_dashboard():
    records = fetch_displaced_families_data()
    total_families = len(records)

    camps_count = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
    shelters_count = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
    other_count = total_families - (camps_count + shelters_count)

    stats = {
        "total": total_families,
        "camps": camps_count,
        "shelters": shelters_count,
        "other": other_count,
    }

    return render_template("home.html", records=records, stats=stats)

@agents_bp.route("/resume", methods=["GET"])
def render_resume():
    raw_records = fetch_displaced_families_data()
    unique_records = []
    seen_ids = set()

    for item in reversed(raw_records):
        nat_id = item.get("national_id") or item.get("id_number")
        if nat_id and nat_id not in seen_ids:
            seen_ids.add(nat_id)
            unique_records.append(item)
        elif not nat_id:
            unique_records.append(item)

    unique_records.reverse()
    return render_template("resume.html", records=unique_records)

@agents_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "module": "AI Agents Module",
        "message": "AI Agents Server is running smoothly"
    }), 200

@agents_bp.route("/query", methods=["POST"])
@agents_bp.route("/api/chat", methods=["POST"])
def process_agent_query():
    data = request.get_json() or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"status": "error", "message": "المسج فارغ"}), 400

    records = fetch_displaced_families_data()
    result = orchestrator.route_and_process(user_message, records)

    return jsonify(result), 200