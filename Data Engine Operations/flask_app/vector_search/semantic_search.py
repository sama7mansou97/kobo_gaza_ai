import math
from vector_search.embeddings import generate_embedding

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """حساب التشابه الدلالي (Cosine Similarity) بين متجهين"""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def search_semantic_records(query: str, records: list[dict], top_k: int = 5) -> list[dict]:
    """
    البحث الدلالي بالنص في قائمة السجلات الميدانية أو سجلات SQLite.
    
    :param query: نص البحث من المستخدم (عربي أو إنجليزي)
    :param records: قائمة السجلات المراد البحث فيها
    :param top_k: عدد أفضل النتائج المطابقة دلالياً
    """
    if not query or not records:
        return []

    # 1. توليد متجه الاستعلام
    query_vector = generate_embedding(query)
    
    results = []

    # 2. حرق أو جلب متجهات السجلات ومقارنتها
    for record in records:
        # تجميع النص الدلالي للسجل (الملاحظات + مكان الإيواء + الحالة)
        text_content = f"{record.get('field_notes', '')} {record.get('description', '')} {record.get('diagnostic_summary', '')} {record.get('shelter_type', '')}"
        
        record_vector = generate_embedding(text_content)
        similarity = cosine_similarity(query_vector, record_vector)
        
        # إضافة الدرجة للسجل
        record_copy = dict(record)
        record_copy['_similarity_score'] = round(similarity, 4)
        results.append(record_copy)

    # 3. ترتيب النتائج تنازلياً حسب درجة التشابه
    results.sort(key=lambda x: x['_similarity_score'], reverse=True)

    return results[:top_k]


if __name__ == "__main__":
    # تجربة سريعة للبحث الدلالي
    mock_records = [
        {"full_name": "أحمد علي", "field_notes": "يعاني من صدمة نفسية حادة وبحاجة لدعم نفسي عاجل"},
        {"full_name": "محمد حسن", "field_notes": "تضرر خيمة الإيواء وبحاجة لمستلزمات خيام طارئة"},
        {"full_name": "سارة أنور", "field_notes": "حالة صحية حرجة وتتطلب رعاية طبية خاصة"},
    ]
    
    search_query = "صدمة نفسية وحالة طوارئ"
    top_matches = search_semantic_records(search_query, mock_records, top_k=2)
    
    print(f"🔍 نتائج البحث الدلالي عن: '{search_query}':")
    for r in top_matches:
        print(f"• {r['full_name']} | نسبة التطابق: {r['_similarity_score']} | الملاحظات: {r['field_notes']}")