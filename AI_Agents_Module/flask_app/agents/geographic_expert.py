import re
from flask_app.agents.base_agent import BaseAgent

def is_english(text: str) -> bool:
    """
    دالة للتحقق مما إذا كان السؤال المكتوب باللغة الإنجليزية
    """
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return english_chars > arabic_chars

def format_en_response(text: str) -> str:
    """
    تغليف النص الإنجليزي في عنصر HTML يفرض الاتجاه من اليسار لليمين
    """
    return f'<div dir="ltr" style="text-align: left; direction: ltr; font-family: system-ui, -apple-system, sans-serif;">{text}</div>'

def format_ar_response(text: str) -> str:
    """
    تغليف النص العربي في عنصر HTML يفرض الاتجاه من اليمين لليمين مع تنسيق متناسق
    """
    return f'<div dir="rtl" style="text-align: right; direction: rtl; font-family: Tajawal, system-ui, sans-serif; line-height: 1.6;">{text}</div>'


class GeographicExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Geographic & Density Expert",
            description="مختص بتحليل الكثافة والتوزيع الجغرافي للأسر المتضررة بين المحافظات والمناطق الفرعية."
        )

    def process_query(self, user_message: str, records: list, lang: str = None, **kwargs) -> str:
        total = len(records)
        
        # الاعتماد على المعامل التلقائي أو فحص لغة النص
        if lang:
            lang_en = (lang.lower() == 'en')
        else:
            lang_en = is_english(user_message)

        if total == 0:
            if lang_en:
                return format_en_response("⚠️ No field records currently available.")
            return format_ar_response("⚠️ لا توجد سجلات ميدانية متاحة حالياً.")

        msg = user_message.lower().strip()
        
        # تفكيك الإحصائيات للمناطق الكبرى والفرعية داخل الجنوب والوسطى
        south_count = 0
        middle_count = 0
        north_count = 0

        # عداد المدن والمناطق الفرعية داخل الجنوب والوسطى والشمال
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
            elif any(x in combined for x in ["middle", "وسطى", "الوسطى"]):
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
            elif any(x in combined for x in ["south", "الجنوب", "جنوب"]):
                south_count += 1

            # إحصاء باقي المناطق للشمال وغزة
            else:
                sub_counts["غزة والشمال"] += 1
                north_count += 1

        # ----------------------------------------------------
        # 1. حالة السؤال الدقيق عن الجنوب ومراكز الاكتظاظ الفرعية فيه
        # ----------------------------------------------------
        if any(k in msg for k in ["جنوب", "الجنوب", "south"]):
            south_sub_ar = {
                "خان يونس": sub_counts["خان يونس"],
                "رفح": sub_counts["رفح"],
                "دير البلح": sub_counts["دير البلح"]
            }
            top_south_city_ar = max(south_sub_ar, key=south_sub_ar.get)
            top_south_count = south_sub_ar[top_south_city_ar]

            city_en_map = {
                "خان يونس": "Khan Younis",
                "رفح": "Rafah",
                "دير البلح": "Deir al-Balah"
            }
            top_south_city_en = city_en_map.get(top_south_city_ar, top_south_city_ar)

            pct_south = round((south_count / total) * 100, 1) if total > 0 else 0

            if lang_en:
                density_str_en = "Very High 🔴" if pct_south >= 35 else ("Medium 🟠" if pct_south >= 15 else "Low 🟢")
                res_en = (
                    f"📍 <b>Population Distribution & Density Report (South Region):</b><br><br>"
                    f"• <b>Total Families Registered in South:</b> {south_count} families out of {total} ({pct_south}%).<br>"
                    f"• <b>General Density Level in South:</b> {density_str_en}<br><br>"
                    f"📊 <b>Density Distribution Across Southern Cities:</b><br>"
                    f"  • <b>Khan Younis:</b> {sub_counts['خان يونس']} families.<br>"
                    f"  • <b>Deir al-Balah:</b> {sub_counts['دير البلح']} families.<br>"
                    f"  • <b>Rafah:</b> {sub_counts['رفح']} families.<br><br>"
                    f"🔥 <b>Highest Concentration Area in South:</b> <b>({top_south_city_en})</b> city with {top_south_count} registered families."
                )
                return format_en_response(res_en)

            density_str_ar = "عالية جداً 🔴" if pct_south >= 35 else ("متوسطة 🟠" if pct_south >= 15 else "منخفضة 🟢")
            res_ar = (
                f"📍 <b>تقرير التوزيع والتمركز السكاني في الجنوب:</b><br><br>"
                f"• <b>إجمالي العائلات المسجلة بالجنوب:</b> {south_count} عائلة من أصل {total} ({pct_south}%).<br>"
                f"• <b>مستوى الكثافة العامة بالجنوب:</b> {density_str_ar}<br><br>"
                f"📊 <b>توزيع الكثافة داخل مدن الجنوب الفرعية:</b><br>"
                f"  • <b>خان يونس:</b> {sub_counts['خان يونس']} عائلة.<br>"
                f"  • <b>دير البلح:</b> {sub_counts['دير البلح']} عائلة.<br>"
                f"  • <b>رفح:</b> {sub_counts['رفح']} عائلة.<br><br>"
                f"🔥 <b>أعلى منطقة اكتظاظ وتمركز بالجنوب:</b> مدينة <b>({top_south_city_ar})</b> بواقع {top_south_count} عائلة مسجلة."
            )
            return format_ar_response(res_ar)

        # ----------------------------------------------------
        # 2. حالة السؤال الدقيق عن المنطقة الوسطى ومخيماتها
        # ----------------------------------------------------
        elif any(k in msg for k in ["وسطى", "الوسطى", "المغازي", "النصيرات", "البريج", "middle", "maghazi", "nuseirat", "bureij"]):
            mid_sub_ar = {
                "النصيرات": sub_counts["النصيرات"],
                "المغازي": sub_counts["المغازي"],
                "البريج": sub_counts["البريج"]
            }
            top_mid_camp_ar = max(mid_sub_ar, key=mid_sub_ar.get)
            top_mid_count = mid_sub_ar[top_mid_camp_ar]

            camp_en_map = {
                "النصيرات": "Nuseirat Camp",
                "المغازي": "Al-Maghazi Camp",
                "البريج": "Al-Bureij Camp"
            }
            top_mid_camp_en = camp_en_map.get(top_mid_camp_ar, top_mid_camp_ar)

            pct_mid = round((middle_count / total) * 100, 1) if total > 0 else 0

            if lang_en:
                density_str_en = "High 🔴" if pct_mid >= 35 else ("Medium 🟠" if pct_mid >= 15 else "Low 🟢")
                res_en = (
                    f"📍 <b>Population Distribution & Density Report (Middle Area):</b><br><br>"
                    f"• <b>Total Families Registered in Middle Area:</b> {middle_count} families out of {total} ({pct_mid}%).<br>"
                    f"• <b>Density Level in Middle Area:</b> {density_str_en}<br><br>"
                    f"📊 <b>Density Distribution Across Central Camps:</b><br>"
                    f"  • <b>Nuseirat Camp:</b> {sub_counts['النصيرات']} families.<br>"
                    f"  • <b>Al-Maghazi Camp:</b> {sub_counts['المغازي']} families.<br>"
                    f"  • <b>Al-Bureij Camp:</b> {sub_counts['البريج']} families.<br><br>"
                    f"🔥 <b>Highest Concentration Camp in Middle Area:</b> <b>({top_mid_camp_en})</b> with {top_mid_count} registered families."
                )
                return format_en_response(res_en)

            density_str_ar = "عالية 🔴" if pct_mid >= 35 else ("متوسطة 🟠" if pct_mid >= 15 else "منخفضة 🟢")
            res_ar = (
                f"📍 <b>تقرير التوزيع والتمركز السكاني في المنطقة الوسطى:</b><br><br>"
                f"• <b>إجمالي العائلات المسجلة بالوسطى:</b> {middle_count} عائلة من أصل {total} ({pct_mid}%).<br>"
                f"• <b>مستوى الكثافة بالمنطقة الوسطى:</b> {density_str_ar}<br><br>"
                f"📊 <b>توزيع الكثافة داخل المخيمات الوسطى الفرعية:</b><br>"
                f"  • <b>مخيم النصيرات:</b> {sub_counts['النصيرات']} عائلة.<br>"
                f"  • <b>مخيم المغازي:</b> {sub_counts['المغازي']} عائلة.<br>"
                f"  • <b>مخيم البريج:</b> {sub_counts['البريج']} عائلة.<br><br>"
                f"🔥 <b>أعلى مخيم اكتظاظاً بالوسطى:</b> مخيم <b>({top_mid_camp_ar})</b> بواقع {top_mid_count} عائلة مسجلة."
            )
            return format_ar_response(res_ar)

        # ----------------------------------------------------
        # 3. التقرير الشامل والمقارنة العامة بين كل المحافظات
        # ----------------------------------------------------
        pct_south = round((south_count / total) * 100, 1) if total > 0 else 0
        pct_mid = round((middle_count / total) * 100, 1) if total > 0 else 0
        pct_north = round((north_count / total) * 100, 1) if total > 0 else 0

        all_regions_ar = {"الجنوب": south_count, "الوسطى": middle_count, "الشمال وغزة": north_count}
        top_overall_ar = max(all_regions_ar, key=all_regions_ar.get)

        region_en_map = {
            "الجنوب": "South (Khan Younis, Deir al-Balah, Rafah)",
            "الوسطى": "Middle Area (Al-Maghazi, Nuseirat, Al-Bureij)",
            "الشمال وغزة": "Gaza City & North Gaza"
        }
        top_overall_en = region_en_map.get(top_overall_ar, top_overall_ar)

        if lang_en:
            res_en = (
                f"📍 <b>Comprehensive Geographical Distribution & Density Report ({total} families):</b><br><br>"
                f"• <b>South (Khan Younis, Rafah, Deir al-Balah):</b> {south_count} families ({pct_south}%).<br>"
                f"• <b>Middle Area (Nuseirat, Maghazi, Bureij):</b> {middle_count} families ({pct_mid}%).<br>"
                f"• <b>North Gaza & Gaza City:</b> {north_count} families ({pct_north}%).<br><br>"
                f"🔥 <b>Most Crowded Region in System:</b> <b>{top_overall_en}</b> with {all_regions_ar[top_overall_ar]} families.<br>"
                f"💡 <b>Field Recommendation:</b> Concentrate food basket and supply distributions in the highest density governorates/cities to cover urgent needs."
            )
            return format_en_response(res_en)

        res_ar = (
            f"📍 <b>تقرير التوزيع الجغرافي والكثافة الميدانية الشامل ({total} عائلة):</b><br><br>"
            f"• <b>الجنوب (خان يونس، رفح، دير البلح):</b> {south_count} عائلة ({pct_south}%).<br>"
            f"• <b>الوسطى (النصيرات، المغازي، البريج):</b> {middle_count} عائلة ({pct_mid}%).<br>"
            f"• <b>الشمال وغزة:</b> {north_count} عائلة ({pct_north}%).<br><br>"
            f"🔥 <b>المحافظة الأكثر اكتظاظاً بالنظام:</b> <b>{top_overall_ar}</b> بواقع {all_regions_ar[top_overall_ar]} عائلة.<br>"
            f"💡 <b>توصية الميدان:</b> تركيز توزيع السلال الغذائية والمستلزمات في المحافظة والمدن الأكثر كثافة لتغطية الاحتياج العاجل."
        )
        return format_ar_response(res_ar)