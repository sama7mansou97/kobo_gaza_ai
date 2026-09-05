 # Documentation - Dashboard Views Module

## Kobo Gaza Relief AI System

---

### 📌 Summary of Completed Tasks

* **Dynamic Kobo API Integration:**
  * **EN:** Built `fetch_displaced_families_data()` function to pull live data dynamically without limiting family counts.
  * **AR:** بناء دالة `fetch_displaced_families_data()` لسحب البيانات الحية والمباشرة ديناميكياً ودون تقييد أعداد الأسر المسجلة.

* **Dashboard Analytics:**
  * **EN:** Created real-time statistics cards for total displaced families, camp residents, and shelter center populations.
  * **AR:** إنشاء بطاقات إحصائية لحظية توضح إجمالي الأسر النازحة، سكان الخيام والمخيمات، وقاطني مراكز الإيواء والمدارس.

* **Data Views & Interface:**
  * **EN:** Designed clean Arabic RTL Bootstrap interface featuring custom tables with badges for family status and needs.
  * **AR:** تصميم واجهة Bootstrap عربية متكاملة (RTL) تتميز بجداول مخصصة وبطاقات ملونة توضح حالة الأسرة واحتياجاتها الميدانية.

---

### 1. Overview / نظرة عامة

* **AR:** يُشكل مجلد **`Dashboard Views`** (والذي يحتوي داخلياً على تطبيق Flask الأساسي `flask_app`) الواجهة الموحدة ونظام العرض التفاعلي للمنظومة. يقوم هذا الجزء بالربط الحي بين بيانات استبيانات KoboToolbox الميدانية وبين نماذج الذكاء الاصطناعي (SPOCS AI Agents) لعرض المؤشرات وتحليل احتياجات النازحين في قطاع غزة بشكل لحظي.
* **EN:** The `Dashboard Views` directory acts as the interactive frontend and visualization layer of the system. It establishes a real-time integration between KoboToolbox survey data and SPOCS AI Agents to render key performance indicators (KPIs) and analyze displacement needs dynamically.

---

### 2. Folder Architecture / البنية الهيكلية للمجلد

kobo_gaza_ai/
├── .vscode/
│   └── launch.json            # إعدادات بيئة العمل والتأكد من تهيئة أدوات التصحيح (Debugger)
├── Dashboard Views/           # المجلد الرئيسي لوجهات لوحة التحكم والتفاصيل
│   ├── documentation/
│   │   └── rubric.md          # مجلد المستندات والتوثيق المرجعي والمعايير
│   └── flask_app/             # الأساسي للوحة التحكم وتطبيق Flask
│       ├── app.py             # نقطة الانطلاق الرئيسية لتشغيل السيرفر والإعدادات
│       ├── routes.py          # معالجة المسارات والربط الحقيقي مع Kobo API للشات والجداول
│       ├── database/          # مجلد إدارة وإعداد قواعد البيانات
│       ├── utils/
│       │   └── llm.py         # محرك معالجة اللغات الطبيعية والاستفسارات الذكية (SPOCS AI)
│       ├── static/            # المرفقات الثابتة الخاصة بالواجهات
│       │   ├── css/
│       │   │   └── style.css  # ملف التنسيقات والأشكال البصرية للموقع
│       │   └── images/        # الصور والشعارات المستخدمة (logo, flag, ruins, q1..q4)
│       └── templates/         # واجهات المستخدم (Jinja2 HTML Templates)
│           ├── layout.html    # الهيكل العام الموحد (Header, Navigation, Footer)
│           ├── home.html      # المؤشرات الرئيسية (KPIs) والسلايدر
│           └── resume.html    # السجل الشامل والشات الذكي المدمج


3. Core Views & Components / المكونات والصفحات الرئيسية
أ. الهيكل الموحد (templates/layout.html)
الوظيفة: يوفر الإطار التفاعلي الموحد لجميع الواجهات.

المميزات:

الهيدر العلوي الذكي مع أزرار التنقل السريع والشعار.

اعتماد خط Tajawal العربي وتضمين مكتبات Bootstrap RTL و FontAwesome.

التذييل السفلي (Footer) المحدث المشتمل على بيانات التواصل، أرقام الدعم الميداني، والبريد الإلكتروني الرسمي (samahmansour97@gmail.com).

ج. السجل الشامل للبيانات والمساعد الذكي (templates/resume.html)
الوظيفة: إدارة واستعلام قاعدة بيانات النازحين بالتفصيل.

المميزات التقنية:

العرض المرن (Pagination/Expand View): يتم عرض أول 5 سجلات تلقائياً لمنع تزاحم الواجهة، مع وجود زر "عرض باقي السجلات" لإظهار بقية البيانات داخل شريط تمرير (Scrollbar) متناسق.

محرك الفلترة والبحث المباشر: تصفية فورية في أعلى الجدول باسم رب الأسرة، رقم الهوية، أو المحافظة والمنطقة.

تنسيق الحالة جغرافياً وإغاثياً: تحويل الرموز اللاتينية من Kobo إلى مسميات عربية دقيقة (مثل: مخيم النصيرات، خان يونس، حالة حادّة/عاجلة).

شات الذكاء الاصطناعي المدمج (Gaza Relief AI Chatbot): شاشة حوار ذكية مدمجة بأسفل الصفحة بمساحة واسعة لعرض الاستعلامات التحليلية المعقدة (مثل: الأسر المسجلة، ذوي الاحتياجات الخاصة، كبار السن، ومناطق الكثافة).

4. Data Handling & Deduplication / معالجة وتصفية البيانات
ربط الـ API: يتم استدعاء البيانات مباشرة من KoboToolbox API عبر routes.py لضمان الحصول على أحدث البيانات الميدانية.

آلية منع التكرار (Deduplication Logic): لمنع تكرار الهويات المسجلة أكثر من مرة، يتم تطبيق تصفية ذكية بحسب رقم الهوية (national_id / id_number) للحفاظ على أحدث سجل فقط لكل رب أسرة:

Python
@main_bp.route("/resume")
def resume():
    raw_records = fetch_displaced_families_data()
    unique_records = []
    seen_ids = set()

    for item in reversed(raw_records):
        nat_id = item.get("national_id") or item.get("id_number")
        if nat_id and nat_id not in seen_ids:
            seen_ids.add(nat_id)
            unique_records.append(item)
        elif not nat_id:
            unique_records.append(item)

    unique_records.reverse()
    return render_template("resume.html", records=unique_records)
5. Execution Command / أمر التشغيل المباشر
Bash
python3 "Dashboard Views/flask_app/app.py"


أسئلة تحليل حالات الإيواء:

"ما هي حالة الإيواء العامة للأسر المسجلة؟"

"كم عدد الأسر المتواجدة داخل الخيام والمخيمات؟"

"كم عدد الأسر التي تقطن في مراكز الإيواء والمدارس؟"

"هل يوجد أسر تعيش في شقق مستأجرة أو استضافة؟"

أسئلة الاحتياجات والحالات الخاصة:

"كم عدد الحالات التي تحتاج إلى دواء ورعاية صحية؟"

"ما هي أبرز الاحتياجات الطبية للأسر النازحة في السجل؟"

"هل توجد أسر ذات احتياجات إغاثية طارئة؟"

أسئلة التوزيع الجغرافي والميداني:

"كيف تتوزع الأسر المسجلة حسب المحافظات والمناطق؟"

"كم عدد الأسر المسجلة في مناطق جنوب القطاع مقارنة بوسط القطاع؟"

"ما هي أكثر المناطق كَثافة بالأسر المتضررة بحسب البيانات؟"


أسئلة الأدوية والاحتياجات الطبية:

"ما هي تفاصيل الاحتياجات الدوائية للأسر؟"

"كم عدد الحالات التي تحتاج أدوية ورعاية صحية؟"

"ما هي أبرز النواقص الطبية في السجل؟"

أسئلة ذوي الاحتياجات الخاصة:

"كم عدد حالات ذوي الاحتياجات الخاصة في السجل؟"

"ما هي احتياجات ذوي الإعاقة وكبار السن؟"

"هل يوجد أسر لديها أفراد من ذوي الهمم؟"