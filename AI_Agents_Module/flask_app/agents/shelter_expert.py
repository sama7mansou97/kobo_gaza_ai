import re
from deep_translator import GoogleTranslator
from flask_app.agents.base_agent import BaseAgent

def is_english(text: str) -> bool:
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return english_chars > arabic_chars

def format_en_response(text: str) -> str:
    """تغليف النص الإنجليزي لمنع تداخل الأسطر وتنسيق الاتجاه من اليسار لليمين"""
    return f'<div dir="ltr" style="text-align: left; direction: ltr; font-family: system-ui, -apple-system, sans-serif;">{text}</div>'

def format_ar_response(text: str) -> str:
    """تغليف النص العربي لتنسيق الاتجاه من اليمين لليمين"""
    return f'<div dir="rtl" style="text-align: right; direction: rtl; font-family: Tajawal, system-ui, sans-serif; line-height: 1.6;">{text}</div>'

def translate_shelter_notes(text: str) -> str:
    """
    ترجمة الملاحظات الميدانية ديناميكياً باستخدام مكتبة deep-translator
    ضمان ترجمة أي نص يدخله الباحث فوراً بدون أي كلمة عربية متبقية
    """
    if not text or not text.strip():
        return ""

    # إذا كان النص لا يحتوي على أي حروف عربية، يُرجع النص كما هو
    if not re.search(r'[\u0600-\u06FF]', text):
        return text.strip()

    try:
        # ترجمة النص آلياً من العربية للإنجليزية
        translated = GoogleTranslator(source='ar', target='en').translate(text.strip())
        
        # تنظيف وتحسين شكل الملاحظة
        translated = re.sub(r'\s*•\s*', ' • ', translated)
        translated = re.sub(r'\s+', ' ', translated).strip()
        return translated
    except Exception as e:
        print(f"Translation Exception: {e}")
        # في حال حدوث خطأ شبكة، يتم تنظيف الأحرف العربية كخيار احتياطي لعدم كسر الواجهة
        clean_fallback = re.sub(r'[\u0600-\u06FF]', '', text).strip()
        return clean_fallback if clean_fallback else "Field note documented in system."


class ShelterExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Shelter & Housing Expert",
            description="مختص بتحليل أنواع السكن والمأوى (خيام، مراكز إيواء، إيجار، استضافة)."
        )

    def process_query(self, user_message: str, records: list, lang: str = None, **kwargs) -> str:
        total = len(records)
        msg = user_message.lower()
        
        if lang:
            is_en = (lang.lower() == 'en')
        else:
            is_en = is_english(user_message)

        if total == 0:
            if is_en:
                return format_en_response("⚠️ No field records currently available.")
            return format_ar_response("⚠️ لا توجد سجلات ميدانية متاحة حالياً.")

        junk_terms = [
            "colab", "تم الرفع", "تسلسل", "aceildehjabyggmeuobqp9", "none", "null", "n/a", 
            "تنبيه ميداني", "رضيع", "حليب", "كرسي", "بتر", "حفاضات", "شلل", "صم", "أدوية", "مرض", "علاج",
            "إعاقة", "اعاقة", "عكاز", "متضرر", "آيل للسقوط"
        ]

        # 1. مطابقة منطق الصفحة الرئيسية (Home Route)
        camps_count = 0
        shelters_count = 0
        other_count = 0

        for item in records:
            shelter_type = str(item.get('shelter_location_type', item.get('shelter_type', item.get('housing_type', '')))).lower()
            
            if any(k in shelter_type for k in ['camp', 'mukhayam', 'tent', 'displacement']):
                camps_count += 1
            elif any(k in shelter_type for k in ['shelter', 'center', 'school', 'center_shelter']):
                shelters_count += 1
            else:
                other_count += 1

        # 2. تحديد نوع الاستعلام
        is_general_query = any(k in msg for k in [
            "ما هي حالة", "حالة المأوى", "وضع السكن", "تقرير المأوى",
            "shelter condition", "housing condition", "shelter status", "housing status"
        ])
        
        is_count_only = any(k in msg for k in ["كم", "عدد", "احصائية", "إحصائية", "how many", "count", "number of"]) and not any(k in msg for k in ["ما هي", "أبرز", "قائمة", "تفاصيل", "اعرض", "ملاحظات", "details", "notes", "show", "list", "primary needs", "needs"])

        # حالة التقرير الشامل
        if is_general_query:
            if is_en:
                res_en = (
                    f"🏠 <b>Comprehensive Shelter & Housing Condition Report for IDPs:</b><br><br>"
                    f"• <b>Total Registered Families:</b> {total} families.<br>"
                    f"• ⛺ <b>Camps & Tents Population:</b> {camps_count} families.<br>"
                    f"• 🏫 <b>Shelter Centers & Schools:</b> {shelters_count} families.<br>"
                    f"• 🏠 <b>Hosted / Other Housing:</b> {other_count} families.<br><br>"
                    f"💡 <b>Field Recommendation:</b> Urgent priority focus on families living in worn-out tents, providing insulating tarpaulins and essential winterization kits."
                )
                return format_en_response(res_en)

            res_ar = (
                f"🏠 <b>تقرير حالة السكن والمأوى الشامل للنازحين:</b><br><br>"
                f"• <b>إجمالي العائلات المسجلة:</b> {total} عائلة.<br>"
                f"• ⛺ <b>الخيام والمخيمات:</b> {camps_count} عائلة.<br>"
                f"• 🏫 <b>مراكز الإيواء والمدارس:</b> {shelters_count} عائلة.<br>"
                f"• 🏠 <b>الشقق والمنازل (إيجار / استضافة / أخرى):</b> {other_count} عائلة.<br><br>"
                f"💡 <b>التوصية الميدانية:</b> التركيز العاجل على العائلات المتواجدة في الخيم المهترئة وتوفير الشوادير العازلة ومستلزمات الشتاء."
            )
            return format_ar_response(res_ar)

        # تحديد الفئات الثلاث
        if any(k in msg for k in ["مدرسة", "مدارس", "مركز إيواء", "مراكز إيواء", "إيواء", "ايواء", "shelter", "shelters", "school", "schools"]):
            matched_cases_count = shelters_count
            category_type = "shelter"
            title_ar = "🏫 <b>تقرير الأسر المتواجدة في مراكز الإيواء والمدارس:</b>"
            title_en = "🏫 <b>Report of Families Located in Shelter Centers & Schools:</b>"
        elif any(k in msg for k in ["خيمة", "خيام", "مخيم", "مخيمات", "tent", "tents", "camp", "camps"]):
            matched_cases_count = camps_count
            category_type = "camp"
            title_ar = "⛺ <b>تقرير الأسر المتواجدة في الخيام والمخيمات:</b>"
            title_en = "⛺ <b>Report of Families Residing in Tents & Displacement Camps:</b>"
        else:
            matched_cases_count = other_count
            category_type = "other"
            title_ar = "🏠 <b>تقرير الأسر المستضافة أو القاطنة في منازل/إيجار:</b>"
            title_en = "🏠 <b>Report of Families Living in Rented Housing or Host Families:</b>"

        # استخراج الملاحظات الميدانية
        extracted_notes = []
        if not is_count_only:
            for item in records:
                shelter_type = str(item.get('shelter_location_type', item.get('shelter_type', item.get('housing_type', '')))).lower()
                
                is_match = False
                if category_type == "camp":
                    is_match = any(k in shelter_type for k in ['camp', 'mukhayam', 'tent', 'displacement'])
                elif category_type == "shelter":
                    is_match = any(k in shelter_type for k in ['shelter', 'center', 'school', 'center_shelter'])
                else:
                    is_match = not any(k in shelter_type for k in ['camp', 'mukhayam', 'tent', 'displacement', 'shelter', 'center', 'school', 'center_shelter'])

                if is_match:
                    for key, val in item.items():
                        if val and (key.endswith("field_notes") or key.endswith("shelter_notes") or key == "notes"):
                            val_str = str(val).strip()
                            val_lower = val_str.lower()
                            if not any(junk in val_lower for junk in junk_terms):
                                extracted_notes.append(val_str)
                                break

        # 3. إرجاع استجابات الإحصاء
        if is_count_only:
            if is_en:
                res_en = (
                    f"{title_en}<br><br>"
                    f"• <b>Total Families Registered in System:</b> {total} families.<br>"
                    f"• <b>Number of Families Matching Housing Category:</b> {matched_cases_count} families."
                )
                return format_en_response(res_en)
            
            res_ar = (
                f"{title_ar}<br><br>"
                f"• <b>إجمالي العائلات المسجلة بالنظام:</b> {total} عائلة.<br>"
                f"• <b>عدد العائلات المطابقة لفئة السكن المطلوبة:</b> {matched_cases_count} عائلة."
            )
            return format_ar_response(res_ar)

        # 4. إرجاع الاستجابات مع التفاصيل والملاحظات المترجمة
        if extracted_notes:
            unique_notes = list(dict.fromkeys(extracted_notes))[:5]
            
            formatted_notes_ar = "<br>".join([f"  • {note}" for note in unique_notes])
            unique_notes_en = [translate_shelter_notes(note) for note in unique_notes]
            formatted_notes_en = "<br>".join([f"  • {note}" for note in unique_notes_en])

            needs_output_ar = f"📋 <b>أبرز الملاحظات الميدانية الخاصة بهذه الفئة:</b><br>{formatted_notes_ar}"
            needs_output_en = f"📋 <b>Primary field notes for this category:</b><br>{formatted_notes_en}"
        else:
            needs_output_ar = "📋 <b>تفاصيل المأوى:</b> بيانات السكن لهذه الفئة مسجلة وتفاصيلها الميدانية موثقة بالاستمارات."
            needs_output_en = "📋 <b>Shelter Details:</b> Housing data for this category is registered and documented in field forms."

        if is_en:
            res_en = (
                f"{title_en}<br><br>"
                f"• <b>Total Families Registered in System:</b> {total} families.<br>"
                f"• <b>Number of Families Matching Housing Category:</b> {matched_cases_count} families.<br><br>"
                f"{needs_output_en}"
            )
            return format_en_response(res_en)

        res_ar = (
            f"{title_ar}<br><br>"
            f"• <b>إجمالي العائلات المسجلة بالنظام:</b> {total} عائلة.<br>"
            f"• <b>عدد العائلات المطابقة لفئة السكن:</b> {matched_cases_count} عائلة.<br><br>"
            f"{needs_output_ar}"
        )
        return format_ar_response(res_ar)