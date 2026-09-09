import os

def call_llm(prompt: str, system_message: str = "أنت مساعد ذكاء اصطناعي خبير في تحليل البيانات الإغاثية لقطاع غزة.") -> str:
    """
    خدمة الاتصال بالذكاء الاصطناعي (مجهزة للاتصال بـ OpenAI / Gemini)
    تُرجع النص المصاغ مباشرة بناءً على التوجيه المعطى.
    """
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # في حال عدم وجود API Key حالياً، يرجع تحليلاً هيكلياً مباشراً
    if not api_key:
        return None

    # هنا يتم تفعيل استدعاء مكتبة الذكاء الاصطناعي المعتمدة
    # مثال: openai.ChatCompletion.create(...)
    return None