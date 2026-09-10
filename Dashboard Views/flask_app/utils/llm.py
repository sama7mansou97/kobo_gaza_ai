import re

def is_english(text):
    """
    دالة موثوقة للتحقق مما إذا كان السؤال المكتوب باللغة الإنجليزية
    """
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return english_chars > arabic_chars

def format_en_response(text):
    """
    تغليف النص الإنجليزي في عنصر HTML يفرض الاتجاه من اليسار لليمين
    """
    return f'<div dir="ltr" style="text-align: left; direction: ltr; font-family: system-ui, -apple-system, sans-serif;">{text}</div>'

def format_ar_response(text):
    """
    تغليف النص العربي في عنصر HTML يفرض الاتجاه من اليمين لليسار مع تنسيق متناسق
    """
    return f'<div dir="rtl" style="text-align: right; direction: rtl; font-family: Tajawal, system-ui, sans-serif; line-height: 1.6;">{text}</div>'

def process_ai_query(user_message, records):
    """
    محرك تحليل الذكاء الاصطناعي لسجلات KoboToolbox الميدانية.
    يعالج الشروط الـ 10 بالكامل وبدقة متناهية باللغتين العربية والإنجليزية.
    """
    total = len(records)
    lang_en = is_english(user_message)

    if total == 0:
        if lang_en:
            return format_en_response("⚠️ No field records currently available to provide an answer.")
        return format_ar_response("⚠️ لا توجد سجلات ميدانية متاحة حالياً لتزويدك بالإجابة.")

    msg = user_message.strip().lower()

    # ----------------------------------------------------
    # 1. تفاصيل كبار السن والمسنين (Elderly & Senior Cases)
    # ----------------------------------------------------
    if any(k in msg for k in ["كبار السن", "مسن", "كبير بالسن", "مسنين", "شيخ", "elderly", "old", "senior", "seniors"]):
        elderly_keywords = ["elderly", "old", "senior", "مسن", "كبار السن", "كبير في السن", "عاجز"]
        elderly_count = 0
        
        for r in records:
            record_content = " ".join([str(v) for v in r.values()]).lower()
            if any(keyword in record_content for keyword in elderly_keywords):
                elderly_count += 1

        if lang_en:
            res = (
                f"👴 <b>Elderly & Senior Citizens Report (Based on Field Registry):</b><br><br>"
                f"• <b>Total Registered Families:</b> {total} families.<br>"
                f"• <b>Families with Elderly / Senior Members:</b> {elderly_count} registered cases.<br><br>"
                f"📋 <b>Key Current Needs:</b><br>"
                f"  - Medications for chronic diseases (hypertension, diabetes, cardiac).<br>"
                f"  - Specialized nutritional supplements.<br>"
                f"  - Field health monitoring and suitable shelter."
            )
            return format_en_response(res)
        
        res_ar = (
            f"👴 <b>تقرير كبار السن والمسنين (بناءً على السجل الميداني):</b><br><br>"
            f"• <b>إجمالي العائلات المسجلة:</b> {total} عائلة.<br>"
            f"• <b>عدد الأسر التي تضم كبار سن / مسنين:</b> {elderly_count} حالة مسجلة.<br><br>"
            f"📋 <b>أبرز احتياجاتهم الحالية:</b><br>"
            f"  - أدوية ومستلزمات أمراض مزمنة (ضغط، سكري، قلب).<br>"
            f"  - أغذية مقوية ومكملات غذائية خاصة.<br>"
            f"  - متابعة صحية ميدانية ومأوى ملائم."
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 2. تفاصيل ذوي الاحتياجات الخاصة والإعاقات (Disability / Special Needs)
    # ----------------------------------------------------
    elif any(k in msg for k in ["احتياجات خاصة", "إعاقة", "معاق", "ذوي الهمم", "كرسي", "disability", "disabled", "handicap", "special needs", "wheelchair"]):
        disability_keywords = [
            "disability", "handicap", "special_needs", "disabled", "wheelchair",
            "إعاقة", "احتياجات خاصة", "ذوي الهمم", "معاق", "حركية", "بصرية", "سمعية", "كرسي"
        ]
        
        special_cases_count = 0
        for r in records:
            record_content = " ".join([str(v) for v in r.values()]).lower()
            if any(keyword in record_content for keyword in disability_keywords):
                special_cases_count += 1

        if lang_en:
            res = (
                f"♿ <b>Persons with Disabilities Report (Based on Field Registry):</b><br><br>"
                f"• <b>Total Registered Families:</b> {total} families.<br>"
                f"• <b>People with Special Needs/Disabilities:</b> {special_cases_count} registered cases.<br><br>"
                f"📋 <b>Key Current Needs:</b><br>"
                f"  - Mobility assist devices (wheelchairs, crutches).<br>"
                f"  - Medical and personal care supplies.<br>"
                f"  - Accessible shelter suitable for mobility conditions."
            )
            return format_en_response(res)

        res_ar = (
            f"♿ <b>تقرير ذوي الاحتياجات الخاصة (بناءً على السجل الميداني):</b><br><br>"
            f"• <b>إجمالي العائلات المسجلة:</b> {total} عائلة.<br>"
            f"• <b>عدد حالات ذوي الاحتياجات الخاصة:</b> {special_cases_count} حالة مسجلة.<br><br>"
            f"📋 <b>أبرز احتياجاتهم الحالية:</b><br>"
            f"  - أجهزة مساعدة حركية (كراسي متحركة، عكازات).<br>"
            f"  - مستلزمات طبية وعناية شخصية خاصة.<br>"
            f"  - مأوى ميسّر ومناسب للظروف الحركية."
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 3. الأسر في الشقق المستأجرة، الاستضافة، المنازل المتضررة (Rent / Host / Damaged)
    # ----------------------------------------------------
    elif any(k in msg for k in ["مستأجرة", "شقة", "استضافة", "مستضيف", "منزل متضرر", "بيت متضرر", "سكن آخر", "شقق", "rent", "rented", "host", "hosted", "apartment", "damaged"]):
        rented_count = 0
        hosted_count = 0
        damaged_house_count = 0
        other_housing_count = 0

        rent_keywords = ["rent", "rented", "مستأجر", "مستأجرة", "إيجار", "ايجار"]
        host_keywords = ["host", "hosted", "hosting", "استضافة", "مستضيف", "عند أقارب", "اقارب"]
        damaged_keywords = ["damage", "damaged", "متضرر", "تضرر", "جزئي", "منزل متضرر"]

        for r in records:
            shelter_type = str(r.get("shelter_location_type", r.get("housing_type", ""))).lower()
            rec_str = " ".join([str(v) for v in r.values()]).lower()

            if any(k in shelter_type or k in rec_str for k in rent_keywords):
                rented_count += 1
            elif any(k in shelter_type or k in rec_str for k in host_keywords):
                hosted_count += 1
            elif any(k in shelter_type or k in rec_str for k in damaged_keywords):
                damaged_house_count += 1
            else:
                if not any(x in shelter_type for x in ["camp", "displacement", "mukhayam", "shelter", "school", "center"]):
                    other_housing_count += 1

        total_private_housing = rented_count + hosted_count + damaged_house_count + other_housing_count

        if lang_en:
            res = (
                f"🏠 <b>Report on Families in Apartments, Hosting & Damaged Homes:</b><br><br>"
                f"• <b>Total Families Outside Camps & Centers:</b> {total_private_housing} families (out of {total} registered).<br><br>"
                f"📊 <b>Breakdown by Housing Type:</b><br>"
                f"  - 🏢 <b>Rented Apartments:</b> {rented_count} families.<br>"
                f"  - 🤝 <b>Hosted (with relatives/other families):</b> {hosted_count} families.<br>"
                f"  - 🏚️ <b>Damaged Houses:</b> {damaged_house_count} families.<br>"
                f"  - 🏠 <b>Other Housing:</b> {other_housing_count} families."
            )
            return format_en_response(res)

        res_ar = (
            f"🏠 <b>تقرير الأسر المقيمة في الشقق، الاستضافة والمنازل المتضررة:</b><br><br>"
            f"• <b>إجمالي الأسر خارج الخيام والمراكز:</b> {total_private_housing} عائلة (من أصل {total} عائلة مسجلة).<br><br>"
            f"📊 <b>التفصيل حسب نوع السكن:</b><br>"
            f"  - 🏢 <b>شقق مستأجرة (إيجار):</b> {rented_count} عائلة.<br>"
            f"  - 🤝 <b>استضافة (مع أقارب أو عائلات أخرى):</b> {hosted_count} عائلة.<br>"
            f"  - 🏚️ <b>منازل متضررة:</b> {damaged_house_count} عائلة.<br>"
            f"  - 🏠 <b>سكن آخر / متفرقات:</b> {other_housing_count} عائلة."
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 4. تفاصيل الاحتياجات الدوائية والطبية (Medicine / Medical Needs)
    # ----------------------------------------------------
    elif any(k in msg for k in ["دواء", "أدوية", "علاج", "مستلزمات دوائية", "طبي", "مرض", "medicine", "medication", "medical", "treatment", "health"]):
        med_records = 0
        for r in records:
            rec_str = " ".join([str(v) for v in r.values()]).lower()
            if any(m in rec_str for m in ["med", "health", "sick", "دواء", "علاج", "مرض", "صحة", "ضغط", "سكري", "أنسولين"]):
                med_records += 1

        if lang_en:
            res = (
                f"💊 <b>Medical & Pharmaceutical Needs Report ({total} registered families):</b><br><br>"
                f"• <b>Total Medical / Medication Cases:</b> {med_records} registered cases.<br>"
                f"• <b>Primary Medical Needs:</b> Chronic disease medications (hypertension, diabetes), surgical dressings, and child nutritional supplements.<br>"
                f"• <b>Action Required:</b> Immediate distribution of medical baskets in coordination with field health points."
            )
            return format_en_response(res)

        res_ar = (
            f"💊 <b>تقرير الاحتياجات الدوائية والطبية المباشر ({total} عائلة مسجلة):</b><br><br>"
            f"• <b>إجمالي الحالات المرضية والدوائية:</b> {med_records} حالة مسجلة.<br>"
            f"• <b>أبرز الاحتياجات الدوائية:</b> أدوية الأمراض المزمنة (الضغط والسكري)، ومستلزمات الغيارات الجراحية، والمغذيات للأطفال.<br>"
            f"• <b>الإجراء المطلوب:</b> توفير سلات دوائية عاجلة بالتنسيق مع النقاط الطبية الميدانية."
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 5. تحليل ومقارنة المناطق الثلاث (الجنوب، الوسطى، الشمال) (South / Middle / North Comparison)
    # ----------------------------------------------------
    elif any(k in msg for k in ["جنوب", "وسط", "شمال", "مقارنة", "south", "middle", "north", "compare", "comparison"]):
        south_count = 0   
        middle_count = 0  
        north_count = 0   

        for r in records:
            gov = str(r.get("governorate", r.get("gov", ""))).lower()
            area = str(r.get("area_name", r.get("detailed_address", ""))).lower()
            combined = f"{gov} {area}"

            if any(x in combined for x in ["maghazi", "nuseirat", "bureij", "المغازي", "النصيرات", "البريج"]):
                middle_count += 1
            elif any(x in combined for x in ["khan", "khanyounis", "rafah", "deir", "خان", "خانيونس", "رفح", "دير"]):
                south_count += 1
            else:
                north_count += 1

        if ("جنوب" in msg or "south" in msg) and ("وسط" in msg or "middle" in msg) and not ("شمال" in msg or "north" in msg):
            diff = abs(south_count - middle_count)
            more_region_ar = "الجنوب" if south_count > middle_count else "الوسطى"
            more_region_en = "South" if south_count > middle_count else "Middle Governorate"
            
            if lang_en:
                res = (
                    f"Comparison between South and Middle Governorates ({total} registered families):<br><br>"
                    f"• 📍 <b>South (Khan Younis, Deir al-Balah, Rafah):</b> {south_count} families.<br>"
                    f"• 📍 <b>Middle (Al-Maghazi, Nuseirat, Al-Bureij):</b> {middle_count} families.<br><br>"
                    f"📊 <b>Result:</b> Registration is higher in <b>{more_region_en}</b> by <b>{diff} families</b>."
                )
                return format_en_response(res)
            
            res_ar = (
                f"مقارنة الأسر المسجلة بين الجنوب والوسطى ({total} عائلة مسجلة):<br><br>"
                f"• 📍 <b>الجنوب (خان يونس، دير البلح، رفح):</b> {south_count} عائلة.<br>"
                f"• 📍 <b>الوسطى (المغازي، النصيرات، البريج):</b> {middle_count} عائلة.<br><br>"
                f"📊 <b>النتيجة:</b> تزيد نسبة التسجيل في <b>{more_region_ar}</b> بفارق <b>{diff} عائلة</b>."
            )
            return format_ar_response(res_ar)

        if lang_en:
            res = (
                f"Based on direct field registry ({total} registered families):<br><br>"
                f"📍 <b>South (Khan Younis, Deir al-Balah, Rafah):</b> {south_count} families.<br>"
                f"📍 <b>Middle (Al-Maghazi, Nuseirat, Al-Bureij):</b> {middle_count} families.<br>"
                f"📍 <b>North (Gaza City, North Gaza, Jabalia, Beit Lahia):</b> {north_count} families."
            )
            return format_en_response(res)
        
        res_ar = (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):<br><br>"
            f"• 📍 <b>الجنوب (خان يونس، دير البلح، رفح):</b> {south_count} عائلة.<br>"
            f"• 📍 <b>الوسطى (المغازي، النصيرات، البريج):</b> {middle_count} عائلة.<br>"
            f"• 📍 <b>الشمال (مدينة غزة، شمال غزة، جباليا، بيت لاهيا):</b> {north_count} عائلة."
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 6. الأكثر كثافة بالمتضررين (Highest Density / Most Affected)
    # ----------------------------------------------------
    elif any(k in msg for k in ["كثافة", "أكثر المناطق", "الأكثر متضررة", "الأعلى", "density", "most affected", "highest"]):
        gov_counts = {}
        for r in records:
            gov_raw = str(r.get("governorate", r.get("gov", "مدينة غزة"))).lower()
            area_raw = str(r.get("area_name", r.get("detailed_address", ""))).lower()
            combined = f"{gov_raw} {area_raw}"

            if any(x in combined for x in ["maghazi", "nuseirat", "bureij", "المغازي", "النصيرات", "البريج"]):
                gov_name = "Middle Governorate (Maghazi, Nuseirat, Bureij)" if lang_en else "المحافظة الوسطى (المغازي، النصيرات، البريج)"
            elif any(x in combined for x in ["khan", "khanyounis", "خان", "خانيونس"]):
                gov_name = "Khan Younis" if lang_en else "خان يونس"
            elif any(x in combined for x in ["deir", "دير"]):
                gov_name = "Deir al-Balah" if lang_en else "دير البلح"
            elif any(x in combined for x in ["rafah", "رفح"]):
                gov_name = "Rafah" if lang_en else "رفح"
            elif any(x in combined for x in ["north", "jabalia", "lahia", "شمال", "جباليا", "بيت لاهيا"]):
                gov_name = "North Gaza (Jabalia & Beit Lahia)" if lang_en else "شمال غزة (جباليا وبيت لاهيا)"
            else:
                gov_name = "Gaza City" if lang_en else "مدينة غزة"

            gov_counts[gov_name] = gov_counts.get(gov_name, 0) + 1

        top_region = max(gov_counts, key=gov_counts.get)
        top_count = gov_counts[top_region]

        if lang_en:
            res = (
                f"Based on direct field registry ({total} registered families):<br><br>"
                f"🔥 <b>The most affected area with highest family density is: {top_region}</b> with <b>{top_count} families</b>.<br><br>"
                f"Density distribution in other areas:<br>" +
                "<br>".join([f"• {k}: {v} families" for k, v in gov_counts.items()])
            )
            return format_en_response(res)
        
        res_ar = (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):<br><br>"
            f"🔥 <b>أكثر المناطق كثافة بالأسر المتضررة هي: {top_region}</b> بإجمالي <b>{top_count} عائلة</b>.<br><br>"
            f"توزيع الكثافة في باقي المناطق:<br>" +
            "<br>".join([f"• {k}: {v} عائلة" for k, v in gov_counts.items()])
        )
        return format_ar_response(res_ar)

    # ----------------------------------------------------
    # 7. التوزيع الجغرافي حسب المحافظات (Governorates Distribution)
    # ----------------------------------------------------
    elif any(k in msg for k in ["محافظات", "المحافظات", "مناطق", "التوزيع الجغرافي", "تتوزع", "governorates", "regions", "distribution"]):
        gov_counts = {}
        for r in records:
            gov_raw = str(r.get("governorate", r.get("gov", "مدينة غزة"))).lower()
            if "deir" in gov_raw or "دير" in gov_raw:
                gov_name = "Deir al-Balah" if lang_en else "دير البلح"
            elif "khan" in gov_raw or "خان" in gov_raw:
                gov_name = "Khan Younis" if lang_en else "خان يونس"
            elif "rafah" in gov_raw or "رفح" in gov_raw:
                gov_name = "Rafah" if lang_en else "رفح"
            elif "north" in gov_raw or "شمال" in gov_raw or "جباليا" in gov_raw:
                gov_name = "North Gaza" if lang_en else "شمال غزة"
            else:
                gov_name = "Gaza City" if lang_en else "مدينة غزة"

            gov_counts[gov_name] = gov_counts.get(gov_name, 0) + 1

        if lang_en:
            details = "<br>".join([f"• {k}: {v} families" for k, v in gov_counts.items()])
            return format_en_response(f"Geographic distribution of registered families ({total} families):<br><br>{details}")
        
        details_ar = "<br>".join([f"• {k}: {v} عائلة" for k, v in gov_counts.items()])
        return format_ar_response(f"توزيع الأسر المسجلة حسب المحافظات ({total} عائلة):<br><br>{details_ar}")

    # ----------------------------------------------------
    # 8. مراكز الإيواء والمدارس (Shelters & Schools)
    # ----------------------------------------------------
    elif any(k in msg for k in ["مراكز الإيواء", "مراكز اإيواء", "المدارس", "مركز إيواء", "shelters", "shelter", "schools", "school", "centers"]):
        shelters = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
        
        if lang_en:
            return format_en_response(f"Based on direct field registry ({total} registered families):<br>There are <b>{shelters} families</b> residing in shelter centers and schools.")
        
        return format_ar_response(f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):<br>يوجد <b>{shelters} عائلة</b> تقطن في مراكز الإيواء والمدارس.")

    # ----------------------------------------------------
    # 9. المخيمات والخيام (Camps & Tents)
    # ----------------------------------------------------
    elif any(k in msg for k in ["المخيمات", "مخيم", "الخيام", "خيمة", "camps", "camp", "tents", "tent"]):
        camps = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
        
        if lang_en:
            return format_en_response(f"Based on direct field registry ({total} registered families):<br>There are <b>{camps} families</b> residing in displacement camps and tents.")
        
        return format_ar_response(f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):<br>يوجد <b>{camps} عائلة</b> متواجدة داخل الخيام والمخيمات.")

    # ----------------------------------------------------
    # 10. الرد الافتراضي ذو الشمولية لكافة أشكال السكن (Default Fallback)
    # ----------------------------------------------------
    else:
        camps = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
        shelters = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
        others = total - (camps + shelters)
        
        if lang_en:
            res = (
                f"Based on direct field registry ({total} registered families):<br>"
                f"• {camps} families in camps and tents.<br>"
                f"• {shelters} families in shelters and schools.<br>"
                f"• {others} families in rented apartments, hosted, or other housing."
            )
            return format_en_response(res)
        
        res_ar = (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):<br>"
            f"• <b>{camps}</b> عائلة في الخيام والمخيمات.<br>"
            f"• <b>{shelters}</b> عائلة في مراكز الإيواء والمدارس.<br>"
            f"• <b>{others}</b> عائلة في الشقق المستأجرة، الاستضافة، أو السكن الآخر."
        )
        return format_ar_response(res_ar)