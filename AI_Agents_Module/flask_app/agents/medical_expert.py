import re
from deep_translator import GoogleTranslator
from flask_app.agents.base_agent import BaseAgent

def is_english(text: str) -> bool:
    """
    دالة للتحقق مما إذا كان السؤال المكتوب باللغة الإنجليزية
    """
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return english_chars > arabic_chars

def format_en_response(text: str) -> str:
    """
    تغليف النص الإنجليزي في عنصر HTML يفرض الاتجاه من اليسار لليمين
    """
    return f'<div dir="ltr" style="text-align: left; direction: ltr; font-family: system-ui, -apple-system, sans-serif;">{text}</div>'

def format_ar_response(text: str) -> str:
    """
    تغليف النص العربي في عنصر HTML يفرض الاتجاه من اليمين لليمين مع تنسيق متناسق
    """
    return f'<div dir="rtl" style="text-align: right; direction: rtl; font-family: Tajawal, system-ui, sans-serif; line-height: 1.6;">{text}</div>'

def translate_medical_text(text: str) -> str:
    """
    ترجمة الحالات والنصوص الطبية الميدانية تلقائياً بدقة باستخدام deep-translator
    """
    if not text or not text.strip():
        return ""

    # إذا كان النص لا يحتوي على أي حروف عربية، يُرجع النص كما هو
    if not re.search(r'[\u0600-\u06FF]', text):
        return text.strip()

    try:
        translated = GoogleTranslator(source='ar', target='en').translate(text.strip())
        translated = re.sub(r'\s*•\s*', ' • ', translated)
        translated = re.sub(r'\s+', ' ', translated).strip()
        return translated
    except Exception as e:
        print(f"Medical Translation Exception: {e}")
        clean_fallback = re.sub(r'[\u0600-\u06FF]', '', text).strip()
        return clean_fallback if clean_fallback else "Medical record documented in system."


class MedicalExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Medical & Health Expert",
            description="مختص بتحليل الحالات الصحية والاحتياجات الدوائية العاجلة."
        )

    def process_query(self, user_message: str, records: list, lang: str = None, **kwargs) -> str:
        total = len(records)
        
        # تحديد اللغة المعتمدة
        if lang:
            lang_en = (lang.lower() == 'en')
        else:
            lang_en = is_english(user_message)

        if total == 0:
            if lang_en:
                return format_en_response("⚠️ No field records currently available.")
            return format_ar_response("⚠️ لا توجد سجلات ميدانية متاحة حالياً.")

        msg = user_message.lower()
        extracted_meds = []
        medical_cases_count = 0

        junk_terms = [
            "colab", "تم الرفع", "تسلسل", "aceildehjabyggmeuobqp9",
            "medical_devices", "chronic_meds", "special_meds", "primary_needs", "none", "null", "n/a",
            "تنبيه ميداني", "تلف كامل", "خيمة", "الأسرة ضمن أولوية"
        ]

        is_bp_diabetes_query = any(k in msg for k in ["ضغط", "سكري", "hypertension", "diabetes", "blood pressure"])

        # تحديد الكلمات المفتاحية والعناوين بناءً على موضوع السؤال واللغة
        if is_bp_diabetes_query:
            target_keywords = ["ضغط", "سكري", "أنسولين", "انسولين", "لانتوس", "كونكور", "hypertension", "diabetes", "insulin", "concor", "lantus"]
            title_ar = "💊 <b>تقرير مرضى الضغط والسكري واحتياجات الأدوية المزمنة:</b>"
            title_en = "💊 <b>Hypertension & Diabetes Patients Chronic Medication Report:</b>"
        elif any(k in msg for k in ["مزمنة", "قلب", "انسولين", "أنسولين", "chronic", "heart", "kidney"]):
            target_keywords = ["مزمن", "قلب", "أنسولين", "انسولين", "كونكور", "لانتوس", "بخاخ", "فنتولين", "كلى", "chronic", "heart", "insulin", "kidney"]
            title_ar = "💊 <b>تقرير الأسر المحتاجة لأدوية الأمراض المزمنة:</b>"
            title_en = "💊 <b>Families Requiring Chronic Illness Medication Report:</b>"
        elif any(k in msg for k in ["أطفال", "حليب", "رضيع", "children", "baby", "infant", "milk"]):
            target_keywords = ["حليب", "أطفال", "اطفال", "رضيع", "خافض حرارة", "milk", "baby", "infant", "children"]
            title_ar = "👶 <b>تقرير الاحتياجات الطبية والغذائية للأطفال والرضع:</b>"
            title_en = "👶 <b>Pediatric & Infant Medical/Nutritional Needs Report:</b>"
        else:
            target_keywords = ["دواء", "علاج", "طبي", "أدوية", "ادوية", "مرض", "انسولين", "أنسولين", "بخاخ", "كونكور", "لانتوس", "مسكنات", "حرارة", "ضغط", "سكري", "medicine", "medication", "treatment", "medical", "drug"]
            title_ar = "💊 <b>تقرير الاحتياجات الطبية والدوائية العاجلة:</b>"
            title_en = "💊 <b>Urgent Medical Care & Medication Needs Report:</b>"

        is_count_only_query = any(k in msg for k in ["كم", "عدد", "احصائية", "إحصائية", "how many", "count", "number of"]) and not any(k in msg for k in ["ما هي", "أبرز", "قائمة", "تفاصيل", "اعرض", "what are", "show", "list", "details"])

        for r in records:
            full_record_text = " ".join([str(v) for v in r.values() if v is not None]).lower()
            
            if any(k in full_record_text for k in target_keywords):
                medical_cases_count += 1
                
                if not is_count_only_query:
                    found_med_text = ""
                    for key, val in r.items():
                        if val is None:
                            continue
                        
                        val_str = str(val).strip()
                        val_lower = val_str.lower()
                        
                        if any(junk in val_lower for junk in junk_terms):
                            continue
                        
                        med_match_keywords = ["دواء", "علاج", "بخاخ", "أنسولين", "انسولين", "حبوب", "مسكن", "كونكور", "لانتوس", "فنتولين", "تبخيرة", "حرارة", "ضغط", "سكري", "حليب", "medication", "medicine", "insulin", "concor", "lantus", "ventolin"]
                        if any(m in val_lower for m in med_match_keywords):
                            if is_bp_diabetes_query:
                                # استبعاد نصوص أدوية الأطفال عند طلب الضغط والسكري
                                parts = [p.strip() for p in val_str.split("+") if not any(x in p.lower() for x in ["طفل", "أطفال", "حرارة", "حليب", "child", "baby", "milk"])]
                                found_med_text = " + ".join(parts) if parts else val_str
                            else:
                                found_med_text = val_str
                            break

                    if found_med_text:
                        extracted_meds.append(found_med_text)

        # 1. حالة الأسئلة الخاصة بالعدد والإحصائيات فقط
        if is_count_only_query:
            if lang_en:
                res_en = (
                    f"{title_en}<br><br>"
                    f"• <b>Total Families Registered in System:</b> {total} families.<br>"
                    f"• <b>Number of Families Matching Medical Query:</b> {medical_cases_count} families."
                )
                return format_en_response(res_en)
            
            res_ar = (
                f"{title_ar}<br><br>"
                f"• <b>إجمالي العائلات المسجلة بالنظام:</b> {total} عائلة.<br>"
                f"• <b>عدد العائلات المطابقة للطلب الطبي:</b> {medical_cases_count} عائلة."
            )
            return format_ar_response(res_ar)

        # 2. حالة الأسئلة التي تتطلب عرض تفاصيل الأدوية والحالات
        if extracted_meds:
            unique_meds = list(dict.fromkeys(extracted_meds))[:5]
            formatted_meds_ar = "<br>".join([f"  • {m}" for m in unique_meds])
            
            # ترجمة الأدوية والحالات الميدانية للغة الإنجليزية تلقائياً
            unique_meds_en = [translate_medical_text(m) for m in unique_meds]
            formatted_meds_en = "<br>".join([f"  • {m}" for m in unique_meds_en])
            
            needs_output_ar = f"📋 <b>أبرز الأدوية والعلاجات المطلوبة صراحة بالاسم:</b><br>{formatted_meds_ar}"
            needs_output_en = f"📋 <b>Most Requested Medications & Treatments Explicitly Named:</b><br>{formatted_meds_en}"
        else:
            needs_output_ar = "📋 <b>تفاصيل الأدوية:</b> مسجلة كاحتياج طبي عاجل في الاستمارات الميدانية."
            needs_output_en = "📋 <b>Medication Details:</b> Registered as urgent medical needs in field forms."

        if lang_en:
            res_en = (
                f"{title_en}<br><br>"
                f"• <b>Total Families Registered in System:</b> {total} families.<br>"
                f"• <b>Number of Families Matching Medical Query:</b> {medical_cases_count} families.<br><br>"
                f"{needs_output_en}"
            )
            return format_en_response(res_en)

        res_ar = (
            f"{title_ar}<br><br>"
            f"• <b>إجمالي العائلات المسجلة بالنظام:</b> {total} عائلة.<br>"
            f"• <b>عدد العائلات المطابقة للطلب الطبي:</b> {medical_cases_count} عائلة.<br><br>"
            f"{needs_output_ar}"
        )
        return format_ar_response(res_ar)