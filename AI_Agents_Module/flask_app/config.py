import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "spocs-ai-agents-secret-key")
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = True
    
    # مفاتيح الربط مع الذكاء الاصطناعي
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")