from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    الفئة الأم الأساسية (Base Class) لجميع وكلاء وخبراء الذكاء الاصطناعي.
    تضمن توحيد الواجهة البرمجية (Interface) لكافة الخبراء مع دعم تعدد اللغات.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def process_query(self, user_message: str, records: list, lang: str = 'ar') -> str:
        """
        دالة المعالجة الرئيسية التي يجب على كل خبير تطبيقها حسب تخصصه.
        :param user_message: نص سؤال أو استفسار المستخدم.
        :param records: قائمة سجلات البيانات الميدانية القادمة من KoBo.
        :param lang: لغة الإجابة المطلوب التوليد بها ('ar' أو 'en').
        :return: الإجابة التحليلية المصاغة باللغة المناسبة.
        """
        pass