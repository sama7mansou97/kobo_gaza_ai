from flask_app.agents.base_agent import BaseAgent

class MedicalExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Medical & Health Expert",
            description="مختص بتحليل الحالات الصحية والاحتياجات الدوائية العاجلة."
        )

    def process_query(self, user_message: str, records: list) -> str:
        total = len(records)
        if total == 0:
            return "⚠️ لا توجد سجلات ميدانية متاحة حالياً."

        msg = user_message.lower()
        extracted_meds = []
        medical_cases_count = 0

        junk_terms = [
            "colab", "تم الرفع", "تسلسل", "aceildehjabyggmeuobqp9",
            "medical_devices", "chronic_meds", "special_meds", "primary_needs", "none", "null", "n/a",
            "تنبيه ميداني", "تلف كامل", "خيمة", "الأسرة ضمن أولوية"
        ]

        is_bp_diabetes_query = "ضغط" in msg or "سكري" in msg

        if is_bp_diabetes_query:
            target_keywords = ["ضغط", "سكري", "أنسولين", "انسولين", "لانتوس", "كونكور"]
            title = "💊 **تقرير مرضى الضغط والسكري واحتياجات الأدوية المزمنة:**"
        elif any(k in msg for k in ["مزمنة", "قلب", "انسولين", "أنسولين"]):
            target_keywords = ["مزمن", "قلب", "أنسولين", "انسولين", "كونكور", "لانتوس", "بخاخ", "فنتولين", "كلى"]
            title = "💊 **تقرير الأسر المحتاجة لأدوية الأمراض المزمنة:**"
        elif any(k in msg for k in ["أطفال", "حليب", "رضيع"]):
            target_keywords = ["حليب", "أطفال", "اطفال", "رضيع", "خافض حرارة"]
            title = "👶 **تقرير الاحتياجات الطبية والغذائية للأطفال والرضع:**"
        else:
            target_keywords = ["دواء", "علاج", "طبي", "أدوية", "ادوية", "مرض", "انسولين", "أنسولين", "بخاخ", "كونكور", "لانتوس", "مسكنات", "حرارة", "ضغط", "سكري"]
            title = "💊 **تقرير الاحتياجات الطبية والدوائية العاجلة:**"

        is_count_only_query = any(k in msg for k in ["كم", "عدد", "احصائية", "إحصائية"]) and not any(k in msg for k in ["ما هي", "أبرز", "قائمة", "تفاصيل", "اعرض"])

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
                        
                        med_match_keywords = ["دواء", "علاج", "بخاخ", "أنسولين", "انسولين", "حبوب", "مسكن", "كونكور", "لانتوس", "فنتولين", "تبخيرة", "حرارة", "ضغط", "سكري", "حليب"]
                        if any(m in val_lower for m in med_match_keywords):
                            if is_bp_diabetes_query:
                                # استبعاد نصوص أدوية الأطفال عند طلب الضغط والسكري
                                parts = [p.strip() for p in val_str.split("+") if not any(x in p.lower() for x in ["طفل", "أطفال", "حرارة", "حليب"])]
                                found_med_text = " + ".join(parts) if parts else val_str
                            else:
                                found_med_text = val_str
                            break

                    if found_med_text:
                        extracted_meds.append(found_med_text)

        if is_count_only_query:
            return (
                f"{title}\n\n"
                f"• **إجمالي العائلات المسجلة بالنظام:** {total} عائلة.\n"
                f"• **عدد العائلات المطابقة للطلب الطبي:** {medical_cases_count} عائلة."
            )

        if extracted_meds:
            unique_meds = list(dict.fromkeys(extracted_meds))[:5]
            formatted_meds = "\n".join([f"  • {m}" for m in unique_meds])
            needs_output = f"📋 **أبرز الأدوية والعلاجات المطلوبة صراحة بالاسم:**\n{formatted_meds}"
        else:
            needs_output = "📋 **تفاصيل الأدوية:** مسجلة كاحتياج طبي عاجل في الاستمارات الميدانية."

        return (
            f"{title}\n\n"
            f"• **إجمالي العائلات المسجلة بالنظام:** {total} عائلة.\n"
            f"• **عدد العائلات المطابقة للطلب الطبي:** {medical_cases_count} عائلة.\n\n"
            f"{needs_output}"
        )