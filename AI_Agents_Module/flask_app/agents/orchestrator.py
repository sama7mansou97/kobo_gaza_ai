import re
from flask_app.agents.geographic_expert import GeographicExpert
from flask_app.agents.shelter_expert import ShelterExpert
from flask_app.agents.medical_expert import MedicalExpert
from flask_app.agents.vulnerability_expert import VulnerabilityExpert

def is_english(text: str) -> bool:
    """دالة فحص لغة السؤال"""
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return english_chars > arabic_chars

class AgentOrchestrator:
    def __init__(self):
        self.geo_agent = GeographicExpert()
        self.shelter_agent = ShelterExpert()
        self.medical_agent = MedicalExpert()
        self.vulner_agent = VulnerabilityExpert()

    def route_and_process(self, user_message: str, records: list, lang: str = None, **kwargs) -> dict:
        msg_lower = user_message.lower()

        # تحديد لغة السؤال
        if lang:
            is_en = (lang.lower() == 'en')
        else:
            is_en = is_english(user_message)

        # ---------------------------------------------------------
        # 1. الكلمات المفتاحية للخبير الجغرافي (عربي + إنجليزي)
        # ---------------------------------------------------------
        geo_keywords = [
            "جغرافي", "جغرافية", "محافظات", "محافظة", "جنوب", "الجنوب", "وسطى", "الوسطى", 
            "شمال", "الشمال", "كثافة", "توزيع", "خان يونس", "رفح", "دير البلح", "المغازي", 
            "النصيرات", "البريج", "غزة", "governorates", "governorate", "location", 
            "region", "density", "geographic", "distribution", "khan yunis", "rafah", "gaza"
        ]
        medical_exclusion = ["علاج", "دواء", "أدوية", "مرضى", "medicine", "medication", "treatment", "medical"]

        if any(k in msg_lower for k in geo_keywords) and not any(k in msg_lower for k in medical_exclusion):
            agent = self.geo_agent
            res = agent.process_query(user_message, records, lang=lang, **kwargs)
            header = f"🤖 **[Processed by: {agent.name}]**\n\n" if is_en else f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n"
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"{header}{res}"
            }

        # ---------------------------------------------------------
        # 2. الكلمات المفتاحية لخبير الصحة والأدوية (عربي + إنجليزي)
        # ---------------------------------------------------------
        medical_keywords = [
            "طبية", "علاج", "أدوية", "ادوية", "مرضى", "طبيب", "أمراض مزمنة", "دواء", "ضغط", "سكري",
            "medicine", "medicines", "medication", "medications", "treatment", "medical", 
            "health", "patients", "chronic", "hypertension", "diabetes", "disease", "drug", "drugs"
        ]
        shelter_exclusion = ["مدرسة", "مأوى", "خيمة", "school", "shelter", "tent"]

        if any(k in msg_lower for k in medical_keywords) and not any(k in msg_lower for k in shelter_exclusion):
            agent = self.medical_agent
            res = agent.process_query(user_message, records, lang=lang, **kwargs)
            header = f"🤖 **[Processed by: {agent.name}]**\n\n" if is_en else f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n"
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"{header}{res}"
            }

        # ---------------------------------------------------------
        # 3. الكلمات المفتاحية لخبير المأوى والسكن (عربي + إنجليزي)
        # ---------------------------------------------------------
        shelter_keywords = [
            "مأوى", "ماوى", "خيمة", "خيام", "مخيم", "مخيمات", "مدرسة", "مدارس", "مركز إيواء", 
            "مراكز إيواء", "إيواء", "ايواء", "استضافة", "سكن", "إيجار", "ايجار", "منازل",
            "shelter", "shelters", "tent", "tents", "camp", "camps", "school", "schools", 
            "housing", "rent", "displacement", "idps"
        ]
        if any(k in msg_lower for k in shelter_keywords):
            agent = self.shelter_agent
            res = agent.process_query(user_message, records, lang=lang, **kwargs)
            header = f"🤖 **[Processed by: {agent.name}]**\n\n" if is_en else f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n"
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"{header}{res}"
            }

        # ---------------------------------------------------------
        # 4. الكلمات المفتاحية لخبير الهشاشة والإعاقة (عربي + إنجليزي)
        # ---------------------------------------------------------
        vulnerability_keywords = [
            "إعاقة", "اعاقة", "إعاقات", "اعاقات", "احتياجات خاصة", "ذوي الهمم",
            "معاق", "مصاب", "مصابين", "إصابة", "اصابة", "عكاز", "كرسي", "أجهزة مساعدة",
            "كبار سن", "طريح", "طريحي", "هشاشة", "الأكثر هشاشة", "ملاحظات الباحث", "طلباتهم", "وفيات", "وفاة", "شهداء", "شهيد",
            "disability", "disabled", "handicapped", "injuries", "injured", "elderly", 
            "vulnerable", "vulnerability", "wheelchair", "special needs", "deaths", "fatalities"
        ]
        if any(k in msg_lower for k in vulnerability_keywords):
            agent = self.vulner_agent
            res = agent.process_query(user_message, records, lang=lang, **kwargs)
            header = f"🤖 **[Processed by: {agent.name}]**\n\n" if is_en else f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n"
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"{header}{res}"
            }

        # ---------------------------------------------------------
        # 5. التوجيه الافتراضي
        # ---------------------------------------------------------
        default_agent = self.vulner_agent
        res = default_agent.process_query(user_message, records, lang=lang, **kwargs)
        header = f"🤖 **[Processed by: {default_agent.name}]**\n\n" if is_en else f"🤖 **[تم المعالجة بواسطة: {default_agent.name}]**\n\n"
        return {
            "status": "success",
            "agent_used": default_agent.name,
            "response": f"{header}{res}"
        }