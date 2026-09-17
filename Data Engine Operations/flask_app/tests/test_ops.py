import unittest
import os
from human_validation.validation_gate import create_pending_action, get_pending_action, clear_pending_action, is_confirmation
from vector_search.embeddings import generate_embedding
from vector_search.semantic_search import cosine_similarity, search_semantic_records
from report_generator.pdf_builder import generate_beneficiary_report

class TestGazaReliefEngine(unittest.TestCase):

    def test_01_validation_gate(self):
        """اختبار بوابة التأكيد البشري"""
        session = "test_user_session"
        create_pending_action(session, "DELETE", "405131029")
        pending = get_pending_action(session)
        
        self.assertIsNotNone(pending)
        self.assertEqual(pending["action"], "DELETE")
        self.assertEqual(pending["target_id"], "405131029")
        self.assertTrue(is_confirmation("نعم"))
        
        clear_pending_action(session)
        self.assertIsNone(get_pending_action(session))

    def test_02_embeddings_and_vector_length(self):
        """اختبار توليد المتجهات وطول 1536-vector"""
        text = "صدمة نفسية ميدانية"
        vec = generate_embedding(text)
        self.assertEqual(len(vec), 1536)

    def test_03_cosine_similarity(self):
        """اختبار حساب التشابه الدلالي"""
        vec1 = generate_embedding("دعم نفسي عاجل")
        vec2 = generate_embedding("دعم نفسي عاجل")
        sim = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(sim, 1.0, places=2)

    def test_04_semantic_search(self):
        """اختبار البحث الدلالي بالسجلات"""
        records = [
            {"head_name": "حسن", "field_notes": "حالة صدمة شديدة بحاجة لرعاية"},
            {"head_name": "محمود", "field_notes": "مستلزمات خيام وإيواء"}
        ]
        results = search_semantic_records("صدمة", records, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["head_name"], "حسن")

    def test_05_pdf_generator(self):
        """اختبار إنشاء تقرير PDF"""
        sample_family = {"head_name": "تجربة اختبار", "national_id": "111222333"}
        pdf_name = "test_output.pdf"
        generated_file = generate_beneficiary_report(sample_family, output_filename=pdf_name)
        
        self.assertTrue(os.path.exists(generated_file))
        if os.path.exists(generated_file):
            os.remove(generated_file)

if __name__ == '__main__':
    print("🧪 بدء تشغيل الفحوصات الآلية الشاملة للمنظومة...\n")
    unittest.main()