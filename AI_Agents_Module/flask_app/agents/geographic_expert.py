from flask_app.agents.base_agent import BaseAgent

class GeographicExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Geographic & Density Expert",
            description="مختص بتحليل الكثافة والتوزيع الجغرافي للأسر المتضررة بين المحافظات والمناطق الفرعية."
        )

    def process_query(self, user_message: str, records: list) -> str:
        total = len(records)
        if total == 0:
            return "⚠️ لا توجد سجلات ميدانية متاحة حالياً."

        msg = user_message.lower()
        
        # تفكيك الإحصائيات للمناطق الكبرى والفرعية داخل الجنوب والوسطى
        south_count = 0
        middle_count = 0
        north_count = 0

        # عداد المدن والمناطق الفرعية داخل الجنوب
        sub_counts = {
            "خان يونس": 0,
            "رفح": 0,
            "دير البلح": 0,
            "النصيرات": 0,
            "المغازي": 0,
            "البريج": 0,
            "غزة والشمال": 0
        }

        for r in records:
            gov = str(r.get("governorate", r.get("gov", ""))).lower()
            area = str(r.get("area_name", r.get("detailed_address", ""))).lower()
            combined = f"{gov} {area} " + " ".join([str(v) for v in r.values() if v]).lower()

            # التحقق من المنطقة الوسطى والمدن الفرعية
            if any(x in combined for x in ["maghazi", "المغازي"]):
                sub_counts["المغازي"] += 1
                middle_count += 1
            elif any(x in combined for x in ["nuseirat", "النصيرات"]):
                sub_counts["النصيرات"] += 1
                middle_count += 1
            elif any(x in combined for x in ["bureij", "البريج"]):
                sub_counts["البريج"] += 1
                middle_count += 1
            elif "الوسطى" in combined:
                middle_count += 1

            # التحقق من الجنوب والمدن الفرعية
            elif any(x in combined for x in ["khan", "khanyounis", "خان", "خانيونس"]):
                sub_counts["خان يونس"] += 1
                south_count += 1
            elif any(x in combined for x in ["rafah", "رفح"]):
                sub_counts["رفح"] += 1
                south_count += 1
            elif any(x in combined for x in ["deir", "دير البلح", "الدير"]):
                sub_counts["دير البلح"] += 1
                south_count += 1
            elif "الجنوب" in combined:
                south_count += 1

            # إحصاء باقي المناطق للشمال وغزة
            else:
                sub_counts["غزة والشمال"] += 1
                north_count += 1

        # 1. حالة السؤال الدقيق عن الجنوب ومراكز الاكتظاظ الفرعية فيه
        if any(k in msg for k in ["جنوب", "الجنوب"]):
            south_sub = {
                "خان يونس": sub_counts["خان يونس"],
                "رفح": sub_counts["رفح"],
                "دير البلح": sub_counts["دير البلح"]
            }
            # تحديد المدينة الأكثر اكتظاظاً بالجنوب
            top_south_city = max(south_sub, key=south_sub.get)
            top_south_count = south_sub[top_south_city]

            pct_south = round((south_count / total) * 100, 1) if total > 0 else 0
            density_str = "عالية جداً 🔴" if pct_south >= 35 else ("متوسطة 🟠" if pct_south >= 15 else "منخفضة 🟢")

            return (
                f"📍 **تقرير التوزيع والتمركز السكاني في الجنوب:**\n\n"
                f"• **إجمالي العائلات المسجلة بالجنوب:** {south_count} عائلة من أصل {total} ({pct_south}%).\n"
                f"• **مستوى الكثافة العامة بالجنوب:** {density_str}\n\n"
                f"📊 **توزيع الكثافة داخل مدن الجنوب الفرعية:**\n"
                f"  • **خان يونس:** {sub_counts['خان يونس']} عائلة.\n"
                f"  • **دير البلح:** {sub_counts['دير البلح']} عائلة.\n"
                f"  • **رفح:** {sub_counts['رفح']} عائلة.\n\n"
                f"🔥 **أعلى منطقة اكتظاظ وتمركز بالجنوب:** مدينة **({top_south_city})** بواقع {top_south_count} عائلة مسجلة."
            )

        # 2. حالة السؤال الدقيق عن المنطقة الوسطى ومخيماتها
        elif any(k in msg for k in ["وسطى", "الوسطى", "المغازي", "النصيرات", "البريج"]):
            mid_sub = {
                "النصيرات": sub_counts["النصيرات"],
                "المغازي": sub_counts["المغازي"],
                "البريج": sub_counts["البريج"]
            }
            top_mid_camp = max(mid_sub, key=mid_sub.get)
            top_mid_count = mid_sub[top_mid_camp]

            pct_mid = round((middle_count / total) * 100, 1) if total > 0 else 0
            density_str = "عالية 🔴" if pct_mid >= 35 else ("متوسطة 🟠" if pct_mid >= 15 else "منخفضة 🟢")

            return (
                f"📍 **تقرير التوزيع والتمركز السكاني في المنطقة الوسطى:**\n\n"
                f"• **إجمالي العائلات المسجلة بالوسطى:** {middle_count} عائلة من أصل {total} ({pct_mid}%).\n"
                f"• **مستوى الكثافة بالمنطقة الوسطى:** {density_str}\n\n"
                f"📊 **توزيع الكثافة داخل المخيمات الوسطى الفرعية:**\n"
                f"  • **مخيم النصيرات:** {sub_counts['النصيرات']} عائلة.\n"
                f"  • **مخيم المغازي:** {sub_counts['المغازي']} عائلة.\n"
                f"  • **مخيم البريج:** {sub_counts['البريج']} عائلة.\n\n"
                f"🔥 **أعلى مخيم اكتظاظاً بالوسطى:** مخيم **({top_mid_camp})** بواقع {top_mid_count} عائلة مسجلة."
            )

        # 3. التقرير الشامل والمقارنة العامة بين كل المحافظات
        pct_south = round((south_count / total) * 100, 1) if total > 0 else 0
        pct_mid = round((middle_count / total) * 100, 1) if total > 0 else 0
        pct_north = round((north_count / total) * 100, 1) if total > 0 else 0

        all_regions = {"الجنوب": south_count, "الوسطى": middle_count, "الشمال وغزة": north_count}
        top_overall = max(all_regions, key=all_regions.get)

        return (
            f"📍 **تقرير التوزيع الجغرافي والكثافة الميدانية الشامل ({total} عائلة):**\n\n"
            f"• **الجنوب (خان يونس، رفح، دير البلح):** {south_count} عائلة ({pct_south}%).\n"
            f"• **الوسطى (النصيرات، المغازي، البريج):** {middle_count} عائلة ({pct_mid}%).\n"
            f"• **الشمال وغزة:** {north_count} عائلة ({pct_north}%).\n\n"
            f"🔥 **المحافظة الأكثر اكتظاظاً بالنظام:** **{top_overall}** بواقع {all_regions[top_overall]} عائلة.\n"
            f"💡 **توصية الميدان:** تركيز توزيع السلال الغذائية والمستلزمات في المحافظة والمدن الأكثر كثافة لتغطية الاحتياج العاجل."
        )