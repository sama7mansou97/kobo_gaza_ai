# Documentation - Four Experts Module
Kobo Gaza Relief AI System
📌 Summary of Completed Tasks
Multi-Agent Architecture Setup:

EN: Initialized four specialized LLM expert roles: Database Read Expert, Database Write Expert, Database Semantic Search Expert, and Orchestrator.

AR: تهيئة أربعة أدوار متخصصة للذكاء الاصطناعي: خبير القراءة، خبير الكتابة، خبير البحث الدلالي، والـ Orchestrator لتنسيق الاستعلامات.

Database Schema & Vector Search Readiness:

EN: Designed llm_roles table and vector embedding structure to enable prompt management and contextual semantic query routing.

AR: تصميم جدول llm_roles وهيكلية تضمين المتجهات (Embeddings) لإدارة المحفزات (Prompts) وتوجيه الاستعلامات الدلالية.

Orchestrator & Human-in-the-Loop Workflow:

EN: Developed query routing logic to split complex user prompts into step-by-step executions and enforce safety confirmations for delete operations.

AR: تطوير منطق التوجيه للـ Orchestrator لتجزئة الاستعلامات المعقدة وتطبيق نظام التأكيد البشري (Human Validation) للعمليات الحساسة كالجمح أو التعديل.

1. Overview / نظرة عامة
AR: يُشكل مجلد Four Experts المحرك الخلفي الذكي ونظام الوكلاء المتعددين (SPOCS AI Agents) للمنظومة. يعمل هذا الجزء بمعزل عن مجلد Dashboard Views ليوفر استجابات دقيقة للاستعلامات المعقدة عبر توزيع المهام بين أربعة خبراء متخصصين (قراءة، كتابة، بحث دلالي، وموجه إداري).

EN: The Four Experts directory houses the multi-agent backend logic. It operates alongside Dashboard Views to resolve complex user intents through a decoupled 4-agent system (Read, Write, Semantic Search, and Orchestrator).

2. Folder Architecture / البنية الهيكلية للمجلد
Plaintext
kobo_gaza_ai/
└── Four Experts/                     # المجلد الرئيسي لموديول الخبراء الأربعة
    ├── .env                          # متغيرات البيئة ومفاتيح الـ API
    ├── prompt_engineering.md          # توثيق تقنيات الهندسة والمحفزات المستخدمة
    ├── Functional Requirements.md     # المتطلبات الوظيفية ومعايير التقييم الخاصة بالموديول
    ├── README.md                     # دليل الاستخدام السريع للـ API والأنظمة
    ├── requirements.txt              # الحزم والمكتبات المعتمدة (Flask, OpenAI, SQLite3)
    ├── app.py                        # نقطة تشغيل سيرفر الـ AI ونقاط النهاية (Endpoints)
    ├── database/                     # إعداد إدارة قواعد بيانات الخبراء
    │   ├── database.py               # دوال الاستعلام والجلب (getLLMRoles, insertRows)
    │   ├── resume.db                 # قاعدة بيانات السير الذاتية والبيانات الميدانية
    │   ├── create_tables/
    │   │   └── llm_roles.sql         # سكربت إنشاء جدول الخبراء والأدوار
    │   └── initial_data/
    │       └── llm_roles.csv         # البيانات الأولية لإعدادات المحفزات والنماذج
    ├── documentation/
    │   └── rubric.md                 # معايير التقييم الأكاديمية والربط المطلوب
    ├── templates/
    │   └── resume.html               # واجهة العرض واختبار الشات التفاعلي للخبراء
    └── utils/                        # الأدوات المساعدة والمحركات
        ├── __init__.py               # حزمة تعريف الموديولات
        ├── llm.py                    # المحرك الرئيسي والقالب الموحد لتوجيه الخبراء
        ├── routes.py                 # معالجة طلبات الـ API والربط مع الشات
        └── socket_events.py          # معالجة الاتصالات اللحظية عبر WebSockets (إن وجدت)
3. Core Agents & Responsibilities / الخبراء الأربعة والمسؤوليات
أ. الموجه الرئيسي (Orchestrator Agent)
الوظيفة: تحليل استعلام المستخدم وتفكيك الطلبات المركبة إلى خطوات تسلسلية توزع على الخبراء.

المميزات:

تنسيق التسلسل: تنفيذ طلبات القراءة ثم الكتابة بالترتيب الصحيح.

التأكيد البشري (Human Validation): إيقاف التنفيذ عند أسلوب الحذف وإظهار طلب confirmation للمستخدم أولاً.

ب. خبير القراءة (Database Read Expert)
الوظيفة: تحويل الأسئلة المباشرة إلى استعلامات SQL SELECT سليمة دون القيام بأي تعديل على قاعدة البيانات.

ج. خبير الكتابة والتعديل (Database Write Expert)
الوظيفة: توليد كود Python تنفيذي ينفذ عمليات الإضافة والتحديث على قاعدة البيانات مباشرة وحفظ البيانات.

د. خبير البحث الدلالي (Database Semantic Search Expert)
الوظيفة: حل الاختصارات المعقدة (مثل تحويل "MSU" إلى "Michigan State University") والبحث في المتجهات (embeddings) لإرجاع النتائج ذات الصلة المعنوية.

4. Integration Logic / آلية الربط دون التعديل على Dashboard Views
الاستدعاء الخارجي الشفاف: يتم استدعاء مخرجات Four Experts برمجياً عبر الـ APIs في routes.py والـ endpoints دون التعديل على أي من ملفات مجلد Dashboard Views.

تحديث الواجهة المباشر: بعد تنفيذ خبير الكتابة لأي إضافة أو تعديل، يتم تحديث واجهة السجل تلقائياً لتعكس البيانات الناتجة فوراً.

5. Execution Command / أمر التشغيل المباشر
Bash
python3 "Four Experts/app.py"