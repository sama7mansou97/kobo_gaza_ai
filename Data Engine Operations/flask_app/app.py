import os
import re
import sys
import requests
import urllib3
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from vector_search.semantic_search import search_semantic_records
from report_generator.pdf_builder import generate_beneficiary_report

# تعطيل تحذيرات التحقق من SSL لطلبات Kobo API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. تحديد المسارات للمشروع والدوال المحلية
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Data Engine Operations/flask_app
ENGINE_DIR = os.path.dirname(CURRENT_DIR)  # Data Engine Operations
BASE_DIR = os.path.dirname(ENGINE_DIR)  # المجلد الرئيسي للمشروع
DASHBOARD_PATH = os.path.join(BASE_DIR, 'Dashboard Views', 'flask_app')

TEMPLATE_FOLDER = os.path.join(DASHBOARD_PATH, 'templates')
STATIC_FOLDER = os.path.join(DASHBOARD_PATH, 'static')

# إضافة مسارات النظام لاستدعاء قاعدة البيانات وبوابة التحقق
for path in [CURRENT_DIR, DASHBOARD_PATH]:
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)

from database.db_manager import (
    delete_patient_records, 
    update_assessment, 
    restore_patient_records
)
from human_validation.validation_gate import (
    clear_pending_action,
    create_pending_action,
    get_pending_action,
)

# 2. إنشاء تطبيق Flask
app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gaza_relief_data_engine_secret')
CORS(app)

# إعدادات الاتصال بـ KoboToolbox API
KOBO_TOKEN = os.getenv('KOBO_API_TOKEN', '34509a89a4e14bf5daf8470e516fe583081274d1')
FORM_ID = os.getenv('KOBO_FORM_ID', 'aceiLDEHJaBYgqMeUoBQP9')

# قائمة السجلات المحذوفة أثناء الجلسة
DELETED_IDS = set()


def fetch_displaced_families_data():
    """جلب السجلات الحية الميدانية من KoboToolbox API مع استبعاد المحذوفات"""
    headers = {
        'Authorization': f'Token {KOBO_TOKEN}',
        'User-Agent': 'Mozilla/5.0',
    }
    url = f'https://eu.kobotoolbox.org/api/v2/assets/{FORM_ID}/data.json?limit=1000'

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [
                r for r in results
                if str(r.get('national_id') or r.get('id_number') or '') not in DELETED_IDS
            ]
    except Exception as e:
        print(f'⚠️ Kobo API Fetch Error: {e}')

    return []


def calculate_stats(records):
    """حساب المؤشرات العامة للاستجابة الميدانية"""
    total_families = len(records)

    camps_count = sum(
        1 for r in records
        if any(x in str(r.get('shelter_location_type', r.get('shelter_type', ''))).lower()
               for x in ['camp', 'displacement', 'mukhayam', 'مخيم', 'خيام'])
    )
    shelters_count = sum(
        1 for r in records
        if any(x in str(r.get('shelter_location_type', r.get('shelter_type', ''))).lower()
               for x in ['shelter', 'center', 'school', 'مدرسة', 'مركز'])
    )
    other_count = max(0, total_families - (camps_count + shelters_count))

    return {
        'total': total_families,
        'camps': camps_count,
        'shelters': shelters_count,
        'other': other_count,
    }


def get_deduplicated_records(raw_records):
    """إزالة تكرار الهويات الوطنية مع الحفاظ على الترتيب الزمني للأحدث"""
    unique_records = []
    seen_ids = set()

    for item in reversed(raw_records):
        nat_id = str(item.get('national_id') or item.get('id_number') or '')
        if nat_id and nat_id not in seen_ids:
            seen_ids.add(nat_id)
            unique_records.append(item)
        elif not nat_id:
            unique_records.append(item)

    unique_records.reverse()
    return unique_records


# -------------------------------------------------------------
# المسارات الأساسية وتوجيه الواجهات
# -------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    """عرض الصفحة الرئيسية واستدعاء قالب home.html وحساب المؤشرات الحية"""
    raw_records = fetch_displaced_families_data()
    unique_records = get_deduplicated_records(raw_records)
    stats = calculate_stats(unique_records)
    return render_template('home.html', records=unique_records, stats=stats)


@app.route('/resume', methods=['GET'])
def resume():
    """عرض السجل الشامل لبيانات النازحين واستدعاء قالب resume.html"""
    raw_records = fetch_displaced_families_data()
    unique_records = get_deduplicated_records(raw_records)
    stats = calculate_stats(unique_records)
    return render_template('resume.html', records=unique_records, stats=stats)


@app.route("/api/chat", methods=["POST"])
def chat_api():
    """مستقبل أسئلة الشات المدمج مع البحث الدلالي والتنسيق ثنائي اللغة وتوليد الـ PDF"""
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    session_id = request.remote_addr

    if not user_message:
        return jsonify({"error": "Please enter a query / الرجاء إدخال نص الاستفسار"}), 400

    is_english = bool(re.search(r'[a-zA-Z]', user_message))

    TRANSLATIONS = {
        "displacement_camp": {"ar": "مخيم نازحين", "en": "Displacement Camp"},
        "shelter_center": {"ar": "مركز إيواء", "en": "Shelter Center"},
        "school": {"ar": "مدرسة إيواء", "en": "School Shelter"},
        "gaza_city": {"ar": "مدينة غزة", "en": "Gaza City"},
        "al_shujaia": {"ar": "الشجاعية", "en": "Al-Shujaia"},
        "al_zeitoun": {"ar": "الزيتون", "en": "Al-Zeitoun"},
        "urgent": {"ar": "عاجل", "en": "Urgent"},
        "normal": {"ar": "عادي", "en": "Normal"},
    }

    def tr(val, lang="ar"):
        val_str = str(val or "").strip()
        if val_str in TRANSLATIONS:
            return TRANSLATIONS[val_str]["en" if lang == "en" else "ar"]
        return val_str if val_str else ("N/A" if lang == "en" else "غير محدد")

    # 1. معالجة التأكيد البشري المعلق
    pending_action = get_pending_action(session_id)
    if pending_action:
        if user_message.lower().strip() in ["نعم", "تأكيد", "موافق", "yes", "confirm"]:
            action = pending_action["action"]
            target_id = str(pending_action["target_id"])
            
            if action == "DELETE":
                delete_patient_records(target_id)
                DELETED_IDS.add(target_id)
                clear_pending_action(session_id)
                msg = f"✅ <b>Record Deleted:</b> All entries for ID (<code>{target_id}</code>) have been permanently removed." if is_english else f"✅ <b>تم الحذف:</b> تم إزالة جميع السجلات للرقم الهويّة (<code>{target_id}</code>) بنجاح."
                return jsonify({"response": msg})
                    
            elif action == "UPDATE":
                new_note = pending_action["payload"].get("new_note", "")
                update_assessment(target_id, new_note, "عاجل")
                clear_pending_action(session_id)
                msg = f"✅ <b>Record Updated:</b> ID (<code>{target_id}</code>) updated with: \"{new_note}\"." if is_english else f"✅ <b>تم التحديث:</b> تم تعديل ملاحظات الهوية (<code>{target_id}</code>) إلى: \"{new_note}\"."
                return jsonify({"response": msg})

        elif user_message.lower().strip() in ["لا", "إلغاء", "no", "cancel"]:
            clear_pending_action(session_id)
            msg = "🚫 <b>Action Cancelled:</b> No changes were made to the records." if is_english else "🚫 <b>تم الإلغاء:</b> لم يتأثر أي سجل بناءً على طلبك."
            return jsonify({"response": msg})
        else:
            msg = f"⚠️ <b>Pending Action:</b> ({pending_action['action']}) for ID (<code>{pending_action['target_id']}</code>). Reply <b>Yes</b> to confirm or <b>No</b> to cancel." if is_english else f"⚠️ <b>عملية معلقة:</b> ({pending_action['action']}) للرقم (<code>{pending_action['target_id']}</code>). أجب بـ <b>نعم</b> للتأكيد أو <b>لا</b> للإلغاء."
            return jsonify({"response": msg})

    # 2. ميزة الاسترجاع (Restore)
    if any(w in user_message.lower() for w in ["استرجاع", "إعادة", "استعادة", "restore", "recover"]):
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            target_id = str(numbers[0])
            if target_id in DELETED_IDS:
                DELETED_IDS.remove(target_id)
            restore_patient_records(target_id)
            msg = f"🔄 <b>Record Restored:</b> National ID (<code>{target_id}</code>) has been successfully re-synced to the database." if is_english else f"🔄 <b>تم الاسترجاع:</b> تم إعادة السجل الخاص برقم الهوية (<code>{target_id}</code>) لقاعدة البيانات."
            return jsonify({"response": msg})
        msg = "⚠️ Please specify the National ID you want to restore." if is_english else "⚠️ يرجى تحديد رقم الهوية المراد استرجاعه."
        return jsonify({"response": msg})

    # 3. طلبات الحذف الجديد (Delete)
    elif any(w in user_message.lower() for w in ["حذف", "مسح", "delete", "remove"]):
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            target_id = str(numbers[0])
            create_pending_action(session_id, "DELETE", target_id)
            msg = f"⚠️ <b>Confirmation Required:</b> Are you sure you want to delete all records for ID (<code>{target_id}</code>)?<br><br>Reply <b>Yes</b> or <b>No</b>." if is_english else f"⚠️ <b>تحذير تأكيد:</b> هل أنت متأكد من رغبتك في حذف كافة السجلات الخاصة برقم الهوية (<code>{target_id}</code>)؟<br><br>أجب بـ <b>نعم</b> للتأكيد أو <b>لا</b> للإلغاء."
            return jsonify({"response": msg})
        msg = "⚠️ Please specify the National ID to delete." if is_english else "⚠️ يرجى تحديد رقم الهوية المطلوب حذفه."
        return jsonify({"response": msg})

    # 4. طلبات التحديث الجديد (Update)
    elif any(w in user_message.lower() for w in ["تحديث", "تعديل", "update", "edit"]):
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            target_id = str(numbers[0])
            new_note = user_message.split("إلى")[-1].strip() if "إلى" in user_message else "Updated field status"
            create_pending_action(session_id, "UPDATE", target_id, {"new_note": new_note})
            msg = f"⚠️ <b>Confirm Update:</b> Change notes for ID (<code>{target_id}</code>) to: <b>\"{new_note}\"</b>?<br><br>Reply <b>Yes</b> or <b>No</b>." if is_english else f"⚠️ <b>تأكيد التعديل:</b> هل أنت متأكد من تحديث سجل رقم الهوية (<code>{target_id}</code>) إلى: <b>\"{new_note}\"</b>؟<br><br>أجب بـ <b>نعم</b> للتأكيد أو <b>لا</b> للإلغاء."
            return jsonify({"response": msg})
        msg = "⚠️ Please state the National ID and the new note." if is_english else "⚠️ يرجى كتابة رقم الهوية والملاحظة الجديدة."
        return jsonify({"response": msg})

    # جلب السجلات الميدانية للعمليات التالية
    raw_records = fetch_displaced_families_data()
    unique_records = get_deduplicated_records(raw_records)
    stats = calculate_stats(unique_records)

    # 5. طلب تصدير تقرير PDF
  # 5. طلب تصدير تقرير PDF عبر الخبراء
    pdf_keywords = ["تقرير", "pdf", "تصدير", "طباعة", "report", "export"]
    if any(k in user_message.lower() for k in pdf_keywords):
        numbers = re.findall(r'\d+', user_message)
        
        # أ) إذا تم تحديد رقم هوية خاص بمستفيد معين
        if numbers:
            target_id = str(numbers[0])
            match = next((r for r in unique_records if str(r.get("national_id") or r.get("id_number") or "") == target_id), None)
            if match:
                pdf_filename = f"report_{target_id}.pdf"
                generate_beneficiary_report(match, unique_records, stats, output_filename=pdf_filename)
                reply = f"📄 <b>تم إنشاء التقرير الفردي بنجاح:</b><br>رقم الهوية: <code>{target_id}</code><br><br>👉 <a href='/download/{pdf_filename}' target='_blank' style='color:#0F766E; font-weight:bold;'>اضغط هنا لتحميل التقرير بصيغة PDF</a>"
                return jsonify({"response": reply})
        
        # ب) إذا كان الطلب عاماً مثل: "بدي تقرير عن التوزيع الجغرافي" أو "بدي تقرير عن المرضى"
        pdf_filename = "expert_summary_report.pdf"
        generate_beneficiary_report(user_message, unique_records, stats, output_filename=pdf_filename)
        reply = f"📄 <b>تم إنشاء تقرير الـ PDF الشامل بناءً على تحليلات الخبراء:</b><br><br>👉 <a href='/download/{pdf_filename}' target='_blank' style='color:#0F766E; font-weight:bold;'>اضغط هنا لتحميل تقرير الذكاء الاصطناعي بصيغة PDF</a>"
        return jsonify({"response": reply})

    
    # 6. البحث الدلالي (Semantic Search)
    semantic_keywords = ["بحث", "دلالي", "حالات", "صدمة", "بحث عن", "search", "semantic", "cases", "trauma"]
    if any(k in user_message.lower() for k in semantic_keywords) and not re.findall(r'\d+', user_message):
        top_matches = search_semantic_records(user_message, unique_records, top_k=3)
        
        if top_matches:
            lang_code = "en" if is_english else "ar"
            reply = "<h3>🔍 Semantic Search Results (Vector Engine)</h3><br>" if is_english else "<h3>🔍 نتائج البحث الدلالي (محرك المتجهات)</h3><br>"
            
            for idx, item in enumerate(top_matches, 1):
                name = item.get("head_name") or item.get("full_name") or "N/A"
                nat_id = str(item.get("national_id") or item.get("id_number") or "N/A")
                notes = tr(item.get("field_notes") or item.get("description"), lang_code)
                score = item.get("_similarity_score", 0.0)
                
                if is_english:
                    reply += f"<b>{idx}. {name}</b> (ID: <code>{nat_id}</code>)<br><b>Similarity Score:</b> <code>{score}</code><br><b>Notes:</b> {notes}<br><br>"
                else:
                    reply += f"<b>{idx}. {name}</b> (الهوية: <code>{nat_id}</code>)<br><b>درجة التطابق الدلالي:</b> <code>{score}</code><br><b>الملاحظات:</b> {notes}<br><br>"
            return jsonify({"response": reply})

    # 7. الأسئلة الإحصائية والبحث المباشر
    if any(w in user_message.lower() for w in ["عدد", "كم", "count", "total", "how many"]):
        if any(w in user_message.lower() for w in ["مخيم", "خيام", "camp"]):
            reply = f"📊 Total families in displacement camps: <b>{stats['camps']}</b> families." if is_english else f"📊 إجمالي عدد الأسر المتواجدة في المخيمات والخيام حالياً: <b>{stats['camps']}</b> عائلة."
        elif any(w in user_message.lower() for w in ["إيواء", "مدارس", "shelter", "school"]):
            reply = f"📊 Total families in shelter centers & schools: <b>{stats['shelters']}</b> families." if is_english else f"📊 إجمالي عدد الأسر المسجلة في مراكز الإيواء والمدارس: <b>{stats['shelters']}</b> عائلة."
        else:
            reply = f"📊 Total registered displaced families: <b>{stats['total']}</b> families." if is_english else f"📊 إجمالي عدد الأسر النازحة والمتضررة المسجلة في النظام: <b>{stats['total']}</b> عائلة."
    else:
        query_numbers = re.findall(r'\d+', user_message)
        search_id = query_numbers[0] if query_numbers else None
        clean_words = [w.lower() for w in re.sub(r'[^\w\s]', '', user_message).split() if w.lower() not in ["ما", "هي", "بيانات", "عن", "سجل", "تفاصيل", "معلومات", "من", "هو", "what", "is", "the", "details", "for", "data"]]
        
        match = None
        for r in unique_records:
            nat_id = str(r.get("national_id") or r.get("id_number") or "")
            head_name = str(r.get("head_name") or r.get("full_name") or "").lower()
            if search_id and search_id == nat_id:
                match = r
                break
            elif clean_words and all(word in head_name for word in clean_words):
                match = r
                break

        if match:
            target_nat_id = str(match.get("national_id") or match.get("id_number") or "")
            lang_code = "en" if is_english else "ar"
            
            name = match.get("head_name") or match.get("full_name") or ("N/A" if is_english else "غير محدد")
            phone = match.get("phone_number") or match.get("mobile_number") or match.get("contact_number") or "0599000000"
            gov = tr(match.get("governorate"), lang_code)
            area = tr(match.get("area_name") or match.get("address_details"), lang_code)
            shelter = tr(match.get("shelter_type") or match.get("shelter_location_type"), lang_code)
            family_members = match.get("family_members_count") or match.get("family_count") or "5"
            notes = tr(match.get("field_notes") or match.get("description"), lang_code)
            submission_time = str(match.get("_submission_time") or match.get("today") or "2026-09-16").split("T")[0]
            uuid = str(match.get("_uuid") or match.get("_id") or "N/A")[:18]

            if is_english:
                reply = (
                    f"<h3>📋 Complete Beneficiary File</h3>"
                    f"<h4>👤 Personal Info:</h4>"
                    f"<b>Name:</b> {name}<br>"
                    f"<b>National ID:</b> <code>{target_nat_id}</code><br>"
                    f"<b>Phone:</b> {phone}<br>"
                    f"<b>Family Members:</b> {family_members}<br><br>"
                    f"<h4>📍 Location & Shelter:</h4>"
                    f"<b>Governorate & Area:</b> {gov} - {area}<br>"
                    f"<b>Shelter Type:</b> {shelter}<br>"
                    f"<b>Field Notes:</b> {notes}<br>"
                    f"<b>Registration Date:</b> {submission_time}<br>"
                    f"<b>Reference UUID:</b> <code>{uuid}</code><br>"
                )
            else:
                reply = (
                    f"<h3>📋 الملف الموحد الكامل للمستفيد</h3>"
                    f"<h4>👤 البيانات الشخصية:</h4>"
                    f"<b>الاسم الرباعي:</b> {name}<br>"
                    f"<b>رقم الهوية:</b> <code>{target_nat_id}</code><br>"
                    f"<b>رقم الهاتف:</b> {phone}<br>"
                    f"<b>عدد الأفراد:</b> {family_members}<br><br>"
                    f"<h4>📍 الموقع والإيواء:</h4>"
                    f"<b>المحافظة والمنطقة:</b> {gov} - {area}<br>"
                    f"<b>مكان الإيواء:</b> {shelter}<br>"
                    f"<b>ملاحظات ميدانية:</b> {notes}<br>"
                    f"<b>تاريخ التسجيل:</b> {submission_time}<br>"
                    f"<b>المعرف المرجعي:</b> <code>{uuid}</code><br>"
                )
        else:
            reply = f"⚠️ No record found matching '{user_message}'." if is_english else f"⚠️ لم يتم العثور على سجل مطابق لـ '{user_message}'."

    return jsonify({"response": reply})


@app.route("/download/<filename>")
def download_file(filename):
    """رابط تنزيل ملفات الـ PDF المولدّة بالمسار الصحيح"""
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return f"⚠️ File not found on server: {filename}", 404


@app.route('/engine/health', methods=['GET'])
def health_check():
    """فحص حالة سيرفر محرك البيانات"""
    return jsonify({
        'status': 'online',
        'module': 'Data Engine Operations',
        'message': 'Data Engine Operations Server is running smoothly',
    }), 200


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5002))
    print(f'🚀 تشغيل سيرفر Data Engine Operations: http://127.0.0.1:{PORT}')
    app.run(host='0.0.0.0', port=PORT, debug=True)