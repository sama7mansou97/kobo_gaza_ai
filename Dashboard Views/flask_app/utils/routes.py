import os
import requests
import urllib3
from flask import Blueprint, jsonify, render_template, request
from utils.llm import process_ai_query

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

main_bp = Blueprint(
    "main",
    __name__,
    template_folder="../templates",
    static_folder="../static",
)

KOBO_TOKEN = os.getenv(
    "KOBO_API_TOKEN", "34509a89a4e14bf5daf8470e516fe583081274d1"
)
FORM_ID = os.getenv("KOBO_FORM_ID", "aceiLDEHJaBYgqMeUoBQP9")


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


@main_bp.route("/")
def home():
    records = fetch_displaced_families_data()
    total_families = len(records)

    camps_count = sum(
        1
        for r in records
        if any(
            x in str(r.get("shelter_location_type", "")).lower()
            for x in ["camp", "displacement", "mukhayam"]
        )
    )
    shelters_count = sum(
        1
        for r in records
        if any(
            x in str(r.get("shelter_location_type", "")).lower()
            for x in ["shelter", "center", "school"]
        )
    )
    other_count = total_families - (camps_count + shelters_count)

    stats = {
        "total": total_families,
        "camps": camps_count,
        "shelters": shelters_count,
        "other": other_count,
    }

    return render_template("home.html", records=records, stats=stats)


@main_bp.route("/resume")
def resume():
    raw_records = fetch_displaced_families_data()
    unique_records = []
    seen_ids = set()

    # التكرار العكسي للبدء بالسجلات الأحدث وتصفية الهويات المكررة
    for item in reversed(raw_records):
        nat_id = item.get("national_id") or item.get("id_number")
        if nat_id and nat_id not in seen_ids:
            seen_ids.add(nat_id)
            unique_records.append(item)
        elif not nat_id:
            unique_records.append(item)

    unique_records.reverse()  # إعادة الترتيب الزمني الأصلي
    return render_template("resume.html", records=unique_records)


# --- مسار الشات المرتبط بنموذج الذكاء الاصطناعي ---
@main_bp.route("/api/chat", methods=["POST"])
def chat_api():
    user_message = request.json.get("message", "")
    records = fetch_displaced_families_data()

    # معالجة الطلب عبر محرك الـ AI بملف llm.py
    ai_response = process_ai_query(user_message, records)

    return jsonify({"response": ai_response})