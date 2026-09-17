# SPOCS AI Agents Module - Rubric & System Architecture

## 1. Overview
يقوم هذا الموديول بإدارة ومعالجة استعلامات الذكاء الاصطناعي الموجهة لنظام تحليل البيانات الإغاثية لقطاع غزة. يعتمد النظام على معماريّة الخبراء المتخصصين (Multi-Agent System) تحت إشراف وكيل منسق (Orchestrator).

---

## 2. Agents Specification & Responsibilities

| Agent / Expert | File Path | Scope & Primary Role |
| :--- | :--- | :--- |
| **Orchestrator** | `agents/orchestrator.py` | تحليل نية المستخدم (Intent Classification)، توجيه الاستعلام للخبير المناسب، ودمج الإجابات النهائية. |
| **Geographic Expert** | `agents/geographic_expert.py` | تحليل البيانات الجغرافية، توزيع الأسر في المحافظات (جنوب، وسطى، شمال)، وتحديد الكثافة الميدانية. |
| **Shelter Expert** | `agents/shelter_expert.py` | تصنيف وتقسيم حالات السكن (خيام، مراكز إيواء، شقق مستأجرة، منازل متضررة) واحتياجات الإيواء. |
| **Medical Expert** | `agents/medical_expert.py` | مسح الحالات الصحية والأمراض المزمنة، وتحديد النواقص والاحتياجات الطبية العاجلة للأسر. |
| **Vulnerability Expert** | `agents/vulnerability_expert.py` | رصد الأسر الأكثر هشاشة (ذوي الهمم، كبار السن، الأيتام، الأسر بلا معيل). |

---

## 3. Technical Evaluation Criteria (Rubric)

### A. Modular Design & Code Quality (30%)
* الفصل التام بين منطق الخبراء (Agents)، خدمات البيانات (`services/`), والـ API Routes (`routes.py`).
* الاعتماد على فئة أم مشتركة (`BaseAgent`) لتوحيد سلوك جميع الخبراء.
* خلو الأكواد من القيم الصلبة (Hardcoded Values) والاعتماد على `config.py`.

### B. Accuracy & Reasoning Quality (40%)
* دقة جلب البيانات وإسقاطها على استفسار المستخدم بدون هلاوس (Hallucinations).
* اتباع أسلوب التفكير المنطقي (Chain-of-Thought) في صياغة الإجابات الميدانية.
* تقديم ردود ملخصة ومباشرة مدعومة بالأرقام والإحصائيات الميدانية الحقيقية.

### C. Integration & Robustness (30%)
* معالجة الأخطاء بشكل سلِس في حال عدم توفر البيانات أو فشل الاتصال بالـ LLM.
* سرعة الاستجابة ومرونة التنسيق بين `Dashboard Views` المجلد الأول وموديول الخبراء الثاني عبر الـ API.

---

## 4. API & Integration Standard
* **Endpoint:** `/api/v1/agent/query`
* **Method:** `POST`
* **Payload Structure:**
  ```json
  {
    "message": "نص استفسار المستخدم",
    "context_data": []
  }

  أسئلة دقيقة مبنية على استمارة KoBo الحقيقية لاختبار الشات:"كم عدد الأسر التي طلبت أدوية أمراض مزمنة أو علاج جروح؟"  "ما هي مقاسات الحفاضات ومراحل حليب الأطفال الأكثر طلباً؟"  "كم عدد الأسر المقيمة في خيام مخرومة أو غير صالحة كلياً؟"  "اعرض لي تفاصيل الأسر المتواجدة في مراكز الإيواء والمدارس."  



pip3 install flask flask-cors
python3 app.py

cd AI_Agents_Module
python3 app.py

cd AI_Agents_Module
python3 app.py

  أسئلة لخبير الهشاشة (VulnerabilityExpert):

"كم عدد حالات ذوي الاحتياجات الخاصة وما هي طلباتهم؟"

"هل يوجد كبار سن أو حالات إعاقة مسجلة في الميدان؟"

أسئلة للخبير الطبي (MedicalExpert):

"ما هي الاحتياجات الدوائية والعلاجية المسجلة للأسر؟"

"كم عدد الحالات المرضية التي تحتاج دواء أو علاج؟"

أسئلة خبير السكن والمأوى (ShelterExpert):

"كم عدد العائلات المتواجدة داخل المخيمات مقارنة بمراكز الإيواء؟"

"ما هي أعداد الأسر المقيمة في الشقق المستأجرة والاستضافة؟"

أسئلة الخبير الجغرافي (GeographicExpert):

"قارن بين أعداد النازحين في الجنوب والمحافظة الوسطى."

"ما هي أكثر المناطق كثافة وتضرراً حسب البيانات الحالية؟"


سئلة لاختبار خبير الهشاشة والإعاقات

"كم عدد حالات ذوي الاحتياجات الخاصة وما هي طلباتهم؟"

"اعرض لي تفاصيل الأسر التي تضم أصحاب إعاقات حركية أو مصابين."

"كم عدد الحالات التي تحتاج أجهزة مساعدة أو كراسي متحركة؟"

"ما هي أبرز ملاحظات الباحث الميدانية الخاصة بالأسر الأكثر هشاشة؟"

"اعرض لي قائمة بالأسر التي تضم كبار سن أو طريحي الفراش وبحاجة لرعاية خاصة."


MedicalExpert
"ما هي أكثر الأدوية والعلاجات المطلوبة من النازحين؟"

"كم عدد العائلات التي تحتاج إلى أدوية أمراض مزمنة؟"

"اعرض لي الحالات التي تحتاج أدوية ورعاية طبية عاجلة."


أسئلة تجريبية لاختبار خبير المأوى (ShelterExpert):
بعد استبدال الكود وإعادة تشغيل السيرفر (python3 app.py)، جربي الأسئلة التالية:

"كم عدد العائلات القاطنة في الخيام والمخيمات؟"

"اعرض لي تفاصيل الأسر المتواجدة في مراكز الإيواء والمدارس."

"ما هي حالة المأوى والسكن للنازحين؟"



. أسئلة اختبار خبير المأوى والسكن (ShelterExpert)
"كم عدد الأسر التي تسكن في منازل بالإيجار أو الاستضافة؟"

"اعرض لي الملاحظات الميدانية للعائلات المقيمة في الخيام."

"كم عدد العائلات المتواجدة في مراكز الإيواء؟"

2. أسئلة اختبار الخبير الجغرافي والكثافة (GeographicExpert)
"ما هو التوزيع الجغرافي للنازحين حسب المحافظات؟"

"كم عدد العائلات المسجلة في المنطقة الوسطى (المغازي، النصيرات، البريج)؟"

"أين تتركز أعلى كثافة للنازحين في الجنوب؟"

3. أسئلة اختبار التوجيه الذكي والدمج بين الوكلاء (اختبار المنسق Orchestrator)
"اعرض لي حصرًا شاملًا لذوي الاحتياجات الخاصة والوفيات."

"كم عدد المرضى الذين يحتاجون إلى أدوية ضغط وسكري؟"

"ما هي أبرز احتياجات العائلات المقيمة في المدارس؟"


"هل يوجد كبار سن أو حالات إعاقة مسجلة في الميدان؟"

"كم عدد حالات ذوي الاحتياجات الخاصة وما هي طلباتهم؟"

كم عدد مرضي الضغط والسكري وما هي الأدوية المطلوبة لهم

ما هي أبرز احتياجات الأسر المتواجدة في المدارس ومراكز الإيواء

أسئلة خبير الصحة والأدوية (MedicalExpert)

"ما هي أكثر الأدوية والعلاجات المطلوبة من النازحين؟"

What are the most requested medicines and medical treatments by IDPs?

"كم عدد العائلات التي تحتاج إلى أدوية أمراض مزمنة؟"

How many families require medications for chronic illnesses?

"اعرض لي الحالات التي تحتاج أدوية ورعاية طبية عاجلة."

Show me the cases requiring urgent medical care and medications.

"كم عدد مرضى الضغط والسكري وما هي الأدوية المطلوبة لهم؟"

How many patients have hypertension and diabetes, and what medications do they need?

أسئلة خبير المأوى والسكن (ShelterExpert)

"كم عدد العائلات القاطنة في الخيام والمخيمات؟"

How many families are living in tents and displacement camps?

"اعرض لي تفاصيل الأسر المتواجدة في مراكز الإيواء والمدارس."

Display the details of families located in shelter centers and schools.

"ما هي حالة المأوى والسكن للنازحين؟"

What is the current shelter and housing condition for IDPs?

"كم عدد الأسر التي تسكن في منازل بالإيجار أو الاستضافة؟"

How many families are living in rented housing or host families?

"اعرض لي الملاحظات الميدانية للعائلات المقيمة في الخيام."

Show me the field notes for families residing in tents.

"كم عدد العائلات المتواجدة في مراكز الإيواء؟"

How many families are residing in shelter centers?

"ما هي أبرز احتياجات الأسر المتواجدة في المدارس ومراكز الإيواء؟"

What are the primary needs of families staying in schools and shelter centers?

أسئلة الخبير الجغرافي والكثافة (GeographicExpert)

"ما هو التوزيع الجغرافي للنازحين حسب المحافظات؟"

What is the geographical distribution of IDPs by governorate?

"كم عدد العائلات المسجلة في المنطقة الوسطى (المغازي، النصيرات، البريج)؟"

How many families are registered in the Middle Area (Al-Maghazi, Nuseirat, Al-Bureij)?

"أين تتركز أعلى كثافة للنازحين في الجنوب؟"

Where is the highest concentration/density of IDPs located in the South?

أسئلة خبير الهشاشة والحالات الخاصة (VulnerabilityExpert)

"هل يوجد كبار سن أو حالات إعاقة مسجلة في الميدان؟"

Are there any elderly people or disability cases registered in the field?

"كم عدد حالات ذوي الاحتياجات الخاصة وما هي طلباتهم؟"

How many cases of people with special needs are recorded, and what are their requests?

أسئلة المنسق الشامل والتوجيه الذكي (Orchestrator)

"اعرض لي حصرًا شاملًا لذوي الاحتياجات الخاصة والوفيات."

"Provide a report on families of martyrs, fatalities, and loss of breadwinner."

"كم عدد المرضى الذين يحتاجون إلى أدوية ضغط وسكري؟"

How many patients require hypertension and diabetes medications?

"ما هي أبرز احتياجات العائلات المقيمة في المدارس؟"

What are the most prominent needs of families residing in schools?



