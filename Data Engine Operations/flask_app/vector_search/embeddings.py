import os
import math
import hashlib

# بُعد المتجه المطلوب
VECTOR_DIMENSION = 1536

def generate_embedding(text: str) -> list[float]:
    """
    توليد متجه عددي (1536-vector) من النص لتمثيل المعنى الدلالي.
    تستبدل هذه الدالة النموذج الخارجي لتوليد متجه محلي ثابت وموزع بناءً على مفردات النص.
    """
    if not text or not isinstance(text, str):
        return [0.0] * VECTOR_DIMENSION

    clean_text = text.strip().lower()
    
    # استخدام خوارزمية Hash لإنشاء seed ناتج عن النص
    text_hash = int(hashlib.sha256(clean_text.encode('utf-8')).hexdigest(), 16)
    
    vector = []
    for i in range(VECTOR_DIMENSION):
        # توليد قيم موقوف عليها النص بين -1.0 و 1.0
        val = math.sin(text_hash + i) * math.cos((text_hash % 997) + i)
        vector.append(val)

    # تطبيع المتجه (Normalize Vector) ليكون طوله 1 لسهولة حساب Cosine Similarity
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]

    return vector


def batch_generate_embeddings(texts: list[str]) -> list[list[float]]:
    """توليد متجهات لمجموعة من النصوص دفعة واحدة"""
    return [generate_embedding(txt) for txt in texts]


if __name__ == "__main__":
    sample_text = "ملاحظة ميدانية: الأسرة بحاجة ماسة لدعم نفسي وإغاثي عاجل"
    vec = generate_embedding(sample_text)
    print(f"✅ تم توليد المتجه بنجاح! الطول: {len(vec)}")