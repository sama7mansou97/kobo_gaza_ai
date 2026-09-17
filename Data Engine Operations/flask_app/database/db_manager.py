import sqlite3
import os
import requests
import urllib3

# تعطيل تحذيرات SSL لطلبات API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# تحديد مسارات قاعدة البيانات والـ Schema
DB_PATH = os.path.join(os.path.dirname(__file__), 'mental_health.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# إعدادات KoboToolbox API
KOBO_TOKEN = os.getenv("KOBO_API_TOKEN", "34509a89a4e14bf5daf8470e516fe583081274d1")
FORM_ID = os.getenv("KOBO_FORM_ID", "aceiLDEHJaBYgqMeUoBQP9")


def get_db_connection():
    """إنشاء اتصال مع قاعدة البيانات مع تفعيل مفاتيح الربط الأجنبي (Foreign Keys)"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول بناءً على schema.sql"""
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()
    print("✅ تم تهيئة قاعدة البيانات والجداول بنجاح.")


def sync_kobo_data_to_db():
    """سحب البيانات الحية من KoboToolbox وحفظها وتحديثها في قاعدة البيانات المحلية SQLite"""
    init_db()  # التأكد من وجود الجداول

    headers = {
        "Authorization": f"Token {KOBO_TOKEN}",
        "User-Agent": "Mozilla/5.0",
    }
    url = f"https://eu.kobotoolbox.org/api/v2/assets/{FORM_ID}/data.json?limit=1000"

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        if response.status_code != 200:
            print(f"❌ فشل سحب بيانات Kobo: رمز الاستجابة {response.status_code}")
            return False

        results = response.json().get("results", [])
        conn = get_db_connection()
        cursor = conn.cursor()

        saved_count = 0
        for item in results:
            nat_id = item.get("national_id") or item.get("id_number")
            if not nat_id:
                continue

            full_name = item.get("head_name") or item.get("full_name") or "غير محدد"
            location = (
                f"{item.get('governorate', '')} - {item.get('area_name', item.get('address_details', ''))}"
            )
            field_notes = item.get("field_notes") or item.get("description") or "لا توجد ملاحظات"
            shelter_type = str(item.get("shelter_location_type") or item.get("shelter_type") or "New")

            # 1. حفظ أو تحديث المستفيد في جدول patients
            cursor.execute("""
                INSERT INTO patients (patient_id, full_name, location)
                VALUES (?, ?, ?)
                ON CONFLICT(patient_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    location = excluded.location
            """, (str(nat_id), str(full_name), str(location)))

            # 2. إضافة سجل الصدمة/الملاحظات الميدانية لجدول trauma_records
            cursor.execute("""
                INSERT INTO trauma_records (patient_id, trauma_type, description)
                VALUES (?, ?, ?)
            """, (str(nat_id), "ملاحظة إغاثية ميدانية", str(field_notes)))

            # 3. إضافة التقييم الأولي في جدول assessments
            cursor.execute("""
                INSERT INTO assessments (patient_id, diagnostic_summary, ptsd_severity, status)
                VALUES (?, ?, ?, ?)
            """, (str(nat_id), str(field_notes), "عاجل" if "urgent" in shelter_type else "عادي", shelter_type))

            saved_count += 1

        conn.commit()
        conn.close()
        print(f"✅ تم مزامنة وحفظ {saved_count} سجل قادم من KoboToolbox في قاعدة البيانات المحلية بنجاح!")
        return True

    except Exception as e:
        print(f"❌ خطأ أثناء مزامنة بيانات Kobo: {e}")
        return False


def delete_patient_records(patient_id):
    """حذف جميع سجلات المستفيد الميدانية من كافة الجداول بعد التأكيد البشري الصريح"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assessments WHERE patient_id = ?", (str(patient_id),))
        cursor.execute("DELETE FROM trauma_records WHERE patient_id = ?", (str(patient_id),))
        cursor.execute("DELETE FROM patients WHERE patient_id = ?", (str(patient_id),))
        conn.commit()
        print(f"🗑️ تم حذف السجلات الخاصة برقم الهوية {patient_id} بنجاح من قاعدة البيانات.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ خطأ أثناء حذف السجل: {e}")
        return False
    finally:
        conn.close()


def restore_patient_records(patient_id):
    """إعادة جلب ومزامنة السجل المحذوف من Kobo إلى قاعدة البيانات المحلية"""
    print(f"🔄 جاري استرجاع السجل رقم الهوية {patient_id}...")
    return sync_kobo_data_to_db()


def update_assessment(patient_id, new_summary, new_severity):
    """تحديث التقييم التشخيصي والميداني لحالة بعد التأكيد البشري الصريح"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE assessments 
            SET diagnostic_summary = ?, ptsd_severity = ?, status = 'Updated'
            WHERE patient_id = ?
        """, (str(new_summary), str(new_severity), str(patient_id)))
        conn.commit()
        print(f"✏️ تم تحديث التقييم والملاحظات برقم الهوية {patient_id} بنجاح.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ خطأ أثناء التحديث: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    
    sync_kobo_data_to_db()
