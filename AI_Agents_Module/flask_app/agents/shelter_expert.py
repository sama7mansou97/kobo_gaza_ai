from flask_app.agents.base_agent import BaseAgent

class ShelterExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Shelter & Housing Expert",
            description="مختص بتحليل أنواع السكن والمأوى (خيام، مراكز إيواء، إيجار، استضافة)."
        )

    def process_query(self, user_message: str, records: list) -> str:
        total = len(records)
        if total == 0:
            return "⚠️ لا توجد سجلات ميدانية متاحة حالياً."

        msg = user_message.lower()
        
        junk_terms = [
            "colab", "تم الرفع", "تسلسل", "aceildehjabyggmeuobqp9", "none", "null", "n/a", 
            "تنبيه ميداني", "رضيع", "حليب", "كرسي", "بتر", "حفاضات", "شلل", "صم", "أدوية", "مرض", "علاج",
            "إعاقة", "اعاقة", "عكاز", "متضرر", "آيل للسقوط"
        ]

        is_general_query = any(k in msg for k in ["ما هي حالة", "حالة المأوى", "وضع السكن", "تقرير المأوى"])
        is_count_only = any(k in msg for k in ["كم", "عدد", "احصائية", "إحصائية"]) and not any(k in msg for k in ["ما هي", "أبرز", "قائمة", "تفاصيل", "اعرض", "ملاحظات"])

        if is_general_query:
            camps_count = sum(1 for r in records if any(k in " ".join([str(v) for v in r.values() if v]).lower() for k in ["خيمة", "خيام", "مخيم", "camp"]))
            shelters_count = sum(1 for r in records if any(k in " ".join([str(v) for v in r.values() if v]).lower() for k in ["مدرسة", "إيواء", "ايواء", "shelter"]))
            hosted_count = sum(1 for r in records if any(k in " ".join([str(v) for v in r.values() if v]).lower() for k in ["إيجار", "ايجار", "استضافة", "شقة"]))
            other_count = max(0, total - (camps_count + shelters_count + hosted_count))

            return (
                f"🏠 **تقرير حالة السكن والمأوى الشامل للنازحين:**\n\n"
                f"• **إجمالي العائلات المسجلة:** {total} عائلة.\n"
                f"• ⛺ **الخيام والمخيمات:** {camps_count} عائلة.\n"
                f"• 🏫 **مراكز الإيواء والمدارس:** {shelters_count} عائلة.\n"
                f"• 🏠 **الشقق والمنازل (إيجار / استضافة):** {hosted_count} عائلة.\n"
                f"• 🏚️ **أشكال سكن أخرى / غير محدد:** {other_count} عائلة.\n\n"
                f"💡 **التوصية الميدانية:** التركيز العاجل على العائلات المتواجدة في الخيم المهترئة وتوفير الشوادير العازلة ومستلزمات الشتاء."
            )

        if any(k in msg for k in ["مدرسة", "مدارس", "مركز إيواء", "مراكز إيواء", "إيواء", "ايواء"]):
            target_keywords = ["مدرسة", "مدارس", "إيواء", "ايواء", "مركز", "shelter"]
            exclude_keywords = ["خيمة", "خيام", "عريشة", "منزل", "شقة", "متضرر"]
            title = "🏫 **تقرير الأسر المتواجدة في مراكز الإيواء والمدارس:**"
        elif any(k in msg for k in ["خيمة", "خيام", "مخيم", "مخيمات"]):
            target_keywords = ["خيمة", "خيام", "مخيم", "camp"]
            exclude_keywords = ["مدرسة", "إيواء"]
            title = "⛺ **تقرير الأسر المتواجدة في الخيام والمخيمات:**"
        else:
            target_keywords = ["إيجار", "ايجار", "استضافة", "مستضيف", "شقة", "منزل"]
            exclude_keywords = ["خيمة", "خيام", "مدرسة"]
            title = "🏠 **تقرير الأسر المستضافة أو القاطنة في منازل/إيجار:**"

        matched_cases_count = 0
        extracted_notes = []

        for r in records:
            full_record_text = " ".join([str(v) for v in r.values() if v is not None]).lower()
            
            if any(k in full_record_text for k in target_keywords) and not any(ex in full_record_text for ex in exclude_keywords):
                matched_cases_count += 1
                
                if not is_count_only:
                    for key, val in r.items():
                        if val and (key.endswith("field_notes") or key.endswith("shelter_notes") or key == "notes"):
                            val_str = str(val).strip()
                            val_lower = val_str.lower()
                            
                            if any(junk in val_lower for junk in junk_terms):
                                continue

                            extracted_notes.append(val_str)
                            break

        if is_count_only:
            return (
                f"{title}\n\n"
                f"• **إجمالي العائلات المسجلة بالنظام:** {total} عائلة.\n"
                f"• **عدد العائلات المطابقة لفئة السكن المطلوبة:** {matched_cases_count} عائلة."
            )

        if extracted_notes:
            unique_notes = list(dict.fromkeys(extracted_notes))[:5]
            formatted_notes = "\n".join([f"  • {note}" for note in unique_notes])
            needs_output = f"📋 **أبرز الملاحظات الميدانية الخاصة بهذه الفئة:**\n{formatted_notes}"
        else:
            needs_output = "📋 **تفاصيل المأوى:** بيانات السكن لهذه الفئة مسجلة وتفاصيلها الميدانية موثقة بالاستمارات."

        return (
            f"{title}\n\n"
            f"• **إجمالي العائلات المسجلة بالنظام:** {total} عائلة.\n"
            f"• **عدد العائلات المطابقة لفئة السكن:** {matched_cases_count} عائلة.\n\n"
            f"{needs_output}"
        )