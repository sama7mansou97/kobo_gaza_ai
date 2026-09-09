from flask_app.agents.geographic_expert import GeographicExpert
from flask_app.agents.shelter_expert import ShelterExpert
from flask_app.agents.medical_expert import MedicalExpert
from flask_app.agents.vulnerability_expert import VulnerabilityExpert

class AgentOrchestrator:
    def __init__(self):
        self.geo_agent = GeographicExpert()
        self.shelter_agent = ShelterExpert()
        self.medical_agent = MedicalExpert()
        self.vulner_agent = VulnerabilityExpert()

    def route_and_process(self, user_message: str, records: list) -> dict:
        msg_lower = user_message.lower()

        # 1. التوجيه للخبير الجغرافي والكثافة أولاً عند وجود كلمات جغرافية صريحة
        geo_keywords = ["جغرافي", "جغرافية", "محافظات", "محافظة", "جنوب", "الجنوب", "وسطى", "الوسطى", "شمال", "الشمال", "كثافة", "توزيع", "خان يونس", "رفح", "دير البلح", "المغازي", "النصيرات", "البريج", "غزة"]
        if any(k in msg_lower for k in geo_keywords) and not any(k in msg_lower for k in ["علاج", "دواء", "أدوية", "مرضى"]):
            agent = GeographicExpert()
            res = agent.process_query(user_message, records)
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n{res}"
            }

        # 2. التوجيه لخبير الصحة والأدوية
        medical_keywords = ["طبية", "علاج", "أدوية", "ادوية", "مرضى", "طبيب", "أمراض مزمنة", "دواء", "ضغط", "سكري"]
        if any(k in msg_lower for k in medical_keywords) and not any(k in msg_lower for k in ["مدرسة", "مأوى", "خيمة"]):
            agent = MedicalExpert()
            res = agent.process_query(user_message, records)
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n{res}"
            }

        # 3. التوجيه لخبير المأوى والسكن
        shelter_keywords = ["مأوى", "ماوى", "خيمة", "خيام", "مخيم", "مخيمات", "مدرسة", "مدارس", "مركز إيواء", "مراكز إيواء", "إيواء", "ايواء", "استضافة", "سكن", "إيجار", "ايجار", "منازل"]
        if any(k in msg_lower for k in shelter_keywords):
            agent = ShelterExpert()
            res = agent.process_query(user_message, records)
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n{res}"
            }

        # 4. توجيه أسئلة الإعاقة، الهامشية، الوفيات إلى خبير الهشاشة
        vulnerability_keywords = [
            "إعاقة", "اعاقة", "إعاقات", "اعاقات", "احتياجات خاصة", "ذوي الهمم",
            "معاق", "مصاب", "مصابين", "إصابة", "اصابة", "عكاز", "كرسي", "أجهزة مساعدة",
            "كبار سن", "طريح", "طريحي", "هشاشة", "الأكثر هشاشة", "ملاحظات الباحث", "طلباتهم", "وفيات", "وفاة", "شهداء", "شهيد"
        ]
        if any(k in msg_lower for k in vulnerability_keywords):
            agent = VulnerabilityExpert()
            res = agent.process_query(user_message, records)
            return {
                "status": "success",
                "agent_used": agent.name,
                "response": f"🤖 **[تم المعالجة بواسطة: {agent.name}]**\n\n{res}"
            }

        # 5. التوجيه الافتراضي
        default_agent = VulnerabilityExpert()
        res = default_agent.process_query(user_message, records)
        return {
            "status": "success",
            "agent_used": default_agent.name,
            "response": f"🤖 **[تم المعالجة بواسطة: {default_agent.name}]**\n\n{res}"
        }