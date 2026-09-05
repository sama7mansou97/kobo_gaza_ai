def process_ai_query(user_message, records):
    """
    محرك تحليل الذكاء الاصطناعي لسجلات KoboToolbox الميدانية.
    يعالج جميع أنواع الاستعلامات عبر شروط متتالية دقيقة.
    """
    total = len(records)
    if total == 0:
        return "⚠️ لا توجد سجلات ميدانية متاحة حالياً لتزويدك بالإجابة."

    msg = user_message.strip().lower()

    # 1. تفاصيل كبار السن (مستقل)
    if any(k in msg for k in ["كبار السن", "مسن", "كبير بالسن", "مسنين", "شيخ"]):
        elderly_keywords = ["elderly", "old", "مسن", "كبار السن", "كبير في السن", "عاجز"]
        elderly_count = 0
        
        for r in records:
            record_content = " ".join([str(v) for v in r.values()]).lower()
            if any(keyword in record_content for keyword in elderly_keywords):
                elderly_count += 1

        return (
            f"👴 **تقرير كبار السن والمسنين (بناءً على السجل الميداني):**\n\n"
            f"• **إجمالي العائلات المسجلة:** {total} عائلة.\n"
            f"• **عدد الأسر التي تضم كبار سن / مسنين:** {elderly_count} حالة مسجلة.\n\n"
            f"📋 **أبرز احتياجاتهم الحالية:**\n"
            f"  - أدوية ومستلزمات أمراض مزمنة (ضغط، سكري، قلب).\n"
            f"  - أغذية مقوية ومكملات غذائية خاصة.\n"
            f"  - متابعة صحية ميدانية ومأوى ملائم."
        )

    # 2. تفاصيل ذوي الاحتياجات الخاصة والإعاقات (مستقل)
    elif any(k in msg for k in ["احتياجات خاصة", "إعاقة", "معاق", "ذوي الهمم", "كرسي"]):
        disability_keywords = [
            "disability", "handicap", "special_needs", "disabled", "wheelchair",
            "إعاقة", "احتياجات خاصة", "ذوي الهمم", "معاق", "حركية", "بصرية", "سمعية", "كرسي"
        ]
        
        special_cases_count = 0
        for r in records:
            record_content = " ".join([str(v) for v in r.values()]).lower()
            if any(keyword in record_content for keyword in disability_keywords):
                special_cases_count += 1

        return (
            f"♿ **تقرير ذوي الاحتياجات الخاصة (بناءً على السجل الميداني):**\n\n"
            f"• **إجمالي العائلات المسجلة:** {total} عائلة.\n"
            f"• **عدد حالات ذوي الاحتياجات الخاصة:** {special_cases_count} حالة مسجلة.\n\n"
            f"📋 **أبرز احتياجاتهم الحالية:**\n"
            f"  - أجهزة مساعدة حركية (كراسي متحركة، عكازات).\n"
            f"  - مستلزمات طبية وعناية شخصية خاصة.\n"
            f"  - مأوى ميسّر ومناسب للظروف الحركية."
        )

    # 3. الأسر في الشقق المستأجرة، الاستضافة، المنازل المتضررة، السكن الآخر
    elif any(k in msg for k in ["مستأجرة", "شقة", "استضافة", "مستضيف", "منزل متضرر", "بيت متضرر", "سكن آخر", "شقق"]):
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
                # حساب أي نوع سكن آخر غير الخيام والمراكز
                if not any(x in shelter_type for x in ["camp", "displacement", "mukhayam", "shelter", "school", "center"]):
                    other_housing_count += 1

        total_private_housing = rented_count + hosted_count + damaged_house_count + other_housing_count

        return (
            f"🏠 **تقرير الأسر المقيمة في الشقق، الاستضافة والمنازل المتضررة:**\n\n"
            f"• **إجمالي الأسر خارج الخيام والمراكز:** {total_private_housing} عائلة (من أصل {total} عائلة مسجلة).\n\n"
            f"📊 **التفصيل حسب نوع السكن:**\n"
            f"  - 🏢 **شقق مستأجرة (إيجار):** {rented_count} عائلة.\n"
            f"  - 🤝 **استضافة (مع أقارب أو عائلات أخرى):** {hosted_count} عائلة.\n"
            f"  - 🏚️ **منازل متضررة:** {damaged_house_count} عائلة.\n"
            f"  - 🏠 **سكن آخر / متفرقات:** {other_housing_count} عائلة."
        )

    # 4. تفاصيل الاحتياجات الدوائية والطبية
    elif any(k in msg for k in ["دواء", "أدوية", "علاج", "مستلزمات دوائية", "طبي", "مرض"]):
        med_records = 0
        for r in records:
            rec_str = " ".join([str(v) for v in r.values()]).lower()
            if any(m in rec_str for m in ["med", "health", "sick", "دواء", "علاج", "مرض", "صحة", "ضغط", "سكري", "أنسولين"]):
                med_records += 1

        return (
            f"💊 **تقرير الاحتياجات الدوائية والطبية المباشر ({total} عائلة مسجلة):**\n\n"
            f"• **إجمالي الحالات المرضية والدوائية:** {med_records} حالة مسجلة.\n"
            f"• **أبرز الاحتياجات الدوائية:** أدوية الأمراض المزمنة (الضغط والسكري)، ومستلزمات الغيارات الجراحية، والمغذيات للأطفال.\n"
            f"• **الإجراء المطلوب:** توفير سلات دوائية عاجلة بالتنسيق مع النقاط الطبية الميدانية."
        )

    # 5. تحليل ومقارنة المناطق الثلاث (الجنوب، الوسطى، الشمال)
    elif any(k in msg for k in ["جنوب", "وسط", "شمال", "مقارنة"]):
        south_count = 0   # خان يونس، دير البلح، رفح
        middle_count = 0  # المغازي، النصيرات، البريج
        north_count = 0   # مدينة غزة، شمال غزة، جباليا، بيت لاهيا

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

        if "جنوب" in msg and "وسط" in msg and not "شمال" in msg:
            diff = abs(south_count - middle_count)
            more_region = "الجنوب" if south_count > middle_count else "الوسطى"
            return (
                f"مقارنة الأسر المسجلة بين الجنوب والوسطى ({total} عائلة مسجلة):\n\n"
                f"• 📍 **الجنوب (خان يونس، دير البلح، رفح):** {south_count} عائلة.\n"
                f"• 📍 **الوسطى (المغازي، النصيرات، البريج):** {middle_count} عائلة.\n\n"
                f"📊 **النتيجة:** تزيد نسبة التسجيل في **{more_region}** بفارق **{diff} عائلة**."
            )

        return (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):\n\n"
            f"📍 **الجنوب (خان يونس، دير البلح، رفح):** {south_count} عائلة.\n"
            f"📍 **الوسطى (المغازي، النصيرات، البريج):** {middle_count} عائلة.\n"
            f"📍 **الشمال (مدينة غزة، شمال غزة، جباليا، بيت لاهيا):** {north_count} عائلة."
        )

    # 6. الأكثر كثافة بالمتضررين
    elif any(k in msg for k in ["كثافة", "أكثر المناطق", "الأكثر متضررة", "الأعلى"]):
        gov_counts = {}
        for r in records:
            gov_raw = str(r.get("governorate", r.get("gov", "مدينة غزة"))).lower()
            area_raw = str(r.get("area_name", r.get("detailed_address", ""))).lower()
            combined = f"{gov_raw} {area_raw}"

            if any(x in combined for x in ["maghazi", "nuseirat", "bureij", "المغازي", "النصيرات", "البريج"]):
                gov_name = "المحافظة الوسطى (المغازي، النصيرات، البريج)"
            elif any(x in combined for x in ["khan", "khanyounis", "خان", "خانيونس"]):
                gov_name = "خان يونس"
            elif any(x in combined for x in ["deir", "دير"]):
                gov_name = "دير البلح"
            elif any(x in combined for x in ["rafah", "رفح"]):
                gov_name = "رفح"
            elif any(x in combined for x in ["north", "jabalia", "lahia", "شمال", "جباليا", "بيت لاهيا"]):
                gov_name = "شمال غزة (جباليا وبيت لاهيا)"
            else:
                gov_name = "مدينة غزة"

            gov_counts[gov_name] = gov_counts.get(gov_name, 0) + 1

        top_region = max(gov_counts, key=gov_counts.get)
        top_count = gov_counts[top_region]

        return (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):\n\n"
            f"🔥 **أكثر المناطق كثافة بالأسر المتضررة هي: {top_region}** بإجمالي **{top_count} عائلة**.\n\n"
            f"توزيع الكثافة في باقي المناطق:\n" +
            "\n".join([f"• {k}: {v} عائلة" for k, v in gov_counts.items()])
        )

    # 7. التوزيع الجغرافي حسب المحافظات
    elif any(k in msg for k in ["محافظات", "المحافظات", "مناطق", "التوزيع الجغرافي", "تتوزع"]):
        gov_counts = {}
        for r in records:
            gov_raw = str(r.get("governorate", r.get("gov", "مدينة غزة"))).lower()
            if "deir" in gov_raw or "دير" in gov_raw:
                gov_name = "دير البلح"
            elif "khan" in gov_raw or "خان" in gov_raw:
                gov_name = "خان يونس"
            elif "rafah" in gov_raw or "رفح" in gov_raw:
                gov_name = "رفح"
            elif "north" in gov_raw or "شمال" in gov_raw or "جباليا" in gov_raw:
                gov_name = "شمال غزة"
            else:
                gov_name = "مدينة غزة"

            gov_counts[gov_name] = gov_counts.get(gov_name, 0) + 1

        details = "\n".join([f"• {k}: {v} عائلة" for k, v in gov_counts.items()])
        return f"توزيع الأسر المسجلة حسب المحافظات ({total} عائلة):\n\n{details}"

    # 8. مراكز الإيواء والمدارس
    elif any(k in msg for k in ["مراكز الإيواء", "مراكز اإيواء", "المدارس", "مركز إيواء"]):
        shelters = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
        return f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):\nيوجد **{shelters} عائلة** تقطن في مراكز الإيواء والمدارس."

    # 9. المخيمات والخيام
    elif any(k in msg for k in ["المخيمات", "مخيم", "الخيام", "خيمة"]):
        camps = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
        return f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):\nيوجد **{camps} عائلة** متواجدة داخل الخيام والمخيمات."

    # 10. الرد الافتراضي ذو الشمولية لكافة أشكال السكن عند عدم فهم السؤال تحديداً
    else:
        camps = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["camp", "displacement", "mukhayam"]))
        shelters = sum(1 for r in records if any(x in str(r.get("shelter_location_type", "")).lower() for x in ["shelter", "center", "school"]))
        others = total - (camps + shelters)
        return (
            f"بناءً على السجل الميداني المباشر ({total} عائلة مسجلة):\n"
            f"• {camps} عائلة في الخيام والمخيمات.\n"
            f"• {shelters} عائلة في مراكز الإيواء والمدارس.\n"
            f"• {others} عائلة في الشقق المستأجرة، الاستضافة، أو السكن الآتي."
        )