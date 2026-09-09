import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KOBO_TOKEN = os.getenv("KOBO_API_TOKEN")
FORM_ID = os.getenv("KOBO_FORM_ID")

def fetch_kobo_records():
    """جلب كافة السجلات الميدانية المباشرة من KoBo API"""
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
        print(f"⚠️ Data Loader Fetch Error: {e}")

    return []

def get_shelter_stats(records):
    """تجهيز إحصائيات السكن والإيواء المباشرة"""
    total = len(records)
    camps = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
    shelters = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
    other = total - (camps + shelters)
    
    return {
        "total": total,
        "camps": camps,
        "shelters": shelters,
        "other": other
    }