import os
import sys
from flask import Blueprint, request, jsonify, render_template

# إضافة مسارات flask_app
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOUR_EXPERTS_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(FOUR_EXPERTS_DIR)
FLASK_APP_DIR = os.path.join(ROOT_DIR, 'Dashboard Views', 'flask_app')

if FLASK_APP_DIR not in sys.path:
    sys.path.insert(0, FLASK_APP_DIR)

# استدعاء دالة جلب البيانات والصفحة الرئيسية من routes الخاص بـ Dashboard Views
try:
    import routes as dashboard_routes
    fetch_displaced_families_data = dashboard_routes.fetch_displaced_families_data
except Exception as e:
    print(f"⚠️ Warning importing dashboard routes: {e}")
    def fetch_displaced_families_data():
        return []

from utils.llm import orchestrator_route

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # عرض الصفحة الرئيسية (المؤشرات والبطاقات الإحصائية)
    raw_records = fetch_displaced_families_data() or []
    return render_template("home.html", records=raw_records)

@main_bp.route('/resume')
def resume():
    # عرض صفحة السجل الشامل والشات المدمج
    raw_records = fetch_displaced_families_data() or []
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

@main_bp.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
        
    # توجيه الطلب إلى الموجه والخبراء الأربعة في Four Experts
    result = orchestrator_route(user_message)
    return jsonify(result)