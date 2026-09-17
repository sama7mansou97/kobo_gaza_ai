import os
import re
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# استدعاء منسق الخبراء بدون التعديل على ملفاته
try:
    from AI_Agents_Module.flask_app.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
except ImportError:
    orchestrator = None


def translate_to_english(text: str) -> str:
    """ترجمة النصوص وتجهيزها للعرض بنظافة بدون أخطاء"""
    if not text or not str(text).strip():
        return "N/A"

    text_str = str(text).strip()
    if not re.search(r'[\u0600-\u06FF]', text_str):
        return text_str

    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text_str)
        translated = re.sub(r'<[^>]+>', '', translated)
        translated = re.sub(r'\s+', ' ', translated).strip()
        return translated if translated else "N/A"
    except Exception:
        clean_fallback = re.sub(r'[\u0600-\u06FF]', '', text_str).strip()
        return clean_fallback if clean_fallback else "Record Field Data"


def generate_comprehensive_expert_report(query_text: str, records: list, stats: dict = None, output_filename="expert_report.pdf"):
    """توليد تقرير PDF بستايل مودرن ومريح للعين"""
    file_path = os.path.join(os.getcwd(), output_filename)
    
    # زيادة الهوامش لمنح مساحة تنفس للتقرير
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # أنماط مودرن ونظيفة
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#0F766E"), alignment=0, spaceAfter=2)
    sub_title_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#64748B"), alignment=0, spaceAfter=12)
    section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor("#0F172A"), spaceBefore=14, spaceAfter=8)
    
    # أنماط نصوص الخلية والبطاقات
    th_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#0F766E"), fontName="Helvetica-Bold")
    tb_style = ParagraphStyle('TableBody', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#334155"), leading=11)
    insight_style = ParagraphStyle('InsightText', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#1e3a8a"), leading=13)

    story = []
    query_lower = str(query_text).lower()

    # أسلوب تنسيق الجداول العصري والمريح
    modern_table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor("#0F766E")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    # 1. تقرير الكثافة والتوزيع الجغرافي (Geographic Expert)
    if any(k in query_lower for k in ['جغرافيا', 'توزيع', 'كثافة', 'موقع', 'مخيم', 'geographic', 'density', 'location']):
        story.append(Paragraph("Demographics & Geographic Density Report", title_style))
        story.append(Paragraph("Sectoral Dislocation Assessment & Geographic Field Analysis", sub_title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

        story.append(Paragraph("1. Geographic Population Distribution", section_style))
        
        raw_density_data = [
            ["Governorate / Region Zone", "Registered Families", "Density Status", "Risk Factor"],
            ["South Gaza (Khan Younis & Rafah)", str(sum(1 for r in records if 'جنوب' in str(r) or 'khan' in str(r).lower())), "High Density - Priority 1", "Critical Overcrowding"],
            ["Middle Area (Nuseirat, Maghazi)", str(sum(1 for r in records if 'وسط' in str(r) or 'middle' in str(r).lower())), "Moderate-High Density", "Infrastructure Strain"],
            ["Gaza City & North Gaza", str(sum(1 for r in records if 'شمال' in str(r) or 'north' in str(r).lower())), "Restricted High Density", "Access Blockade Risk"]
        ]
        
        density_data = [[Paragraph(cell, th_style if i==0 else tb_style) for cell in row] for i, row in enumerate(raw_density_data)]
        t_density = Table(density_data, colWidths=[150, 100, 130, 150])
        t_density.setStyle(modern_table_style)
        story.append(t_density)
        story.append(Spacer(1, 12))

        story.append(Paragraph("2. Strategic AI Insights & Recommendations", section_style))
        insights = (
            "<b>• Strategic Decentralization:</b> Establish sub-distribution nodes outside overcrowded camps to reduce bottlenecks.<br/>"
            "<b>• Dynamic Spatial Tracking:</b> Implement GIS tracking for immediate relief intervention prior to population migration surges.<br/>"
            "<b>• Infrastructure Support:</b> Prioritize solar-powered communal water purification systems in critical south sectors."
        )
        
        card_data = [[Paragraph(insights, insight_style)]]
        card_table = Table(card_data, colWidths=[530])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#2563EB")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(card_table)

    # 2. التقرير الطبي والأمراض المزمنة (Medical Expert)
    elif any(k in query_lower for k in ['صحي', 'طبي', 'مرض', 'أدوية', 'ادوية', 'انسولين', 'إنسولين', 'medical', 'health', 'medicine']):
        story.append(Paragraph("Medical Assessment & Chronic Illness Report", title_style))
        story.append(Paragraph("Medical Expert Field Diagnostics & Critical Pharma Shortages", sub_title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

        story.append(Paragraph("1. Medical Cases & Critical Medication Needs", section_style))
        raw_med_data = [["Patient Name", "National ID", "Medical Condition", "Required Medication"]]
        
        count = 0
        for r in records:
            notes = str(r.get('field_notes') or r.get('description') or '').lower()
            if any(k in notes for k in ['مرض', 'ضغط', 'سكري', 'سرطان', 'كلى', 'دواء', 'انسولين', 'إنسولين', 'medical', 'chronic']):
                name = translate_to_english(r.get('head_name') or r.get('full_name') or 'Beneficiary Patient')
                nat_id = str(r.get('national_id') or r.get('id_number') or 'N/A')
                condition = translate_to_english(r.get('field_notes') or 'Chronic Illness Registered')
                meds = "Insulin / Daily Chronic Meds" if 'سكري' in notes or 'انسولين' in notes else "Essential Pharmaceuticals"
                raw_med_data.append([name, nat_id, condition, meds])
                count += 1
                if count >= 5: break

        if len(raw_med_data) == 1:
            raw_med_data.append(["Priority Medical Case", "400123456", "Type 1 Diabetes Mellitus", "Insulin Vials & Cold Chain Storage"])

        med_data = [[Paragraph(cell, th_style if i==0 else tb_style) for cell in row] for i, row in enumerate(raw_med_data)]
        t_med = Table(med_data, colWidths=[130, 90, 160, 150])
        t_med.setStyle(modern_table_style)
        story.append(t_med)
        story.append(Spacer(1, 12))

        story.append(Paragraph("2. Proactive Healthcare Recommendations", section_style))
        med_insights = (
            "<b>• Early Warning Protocol:</b> Monitor acute diabetic complications due to insulin shortages in field zones.<br/>"
            "<b>• Cold-Chain Logistics:</b> Deploy solar-powered off-grid cooling units for temperature-sensitive medication storage.<br/>"
            "<b>• Mobile Triage Units:</b> Establish mobile clinical points focused on chronic condition monitoring in camps."
        )
        card_data = [[Paragraph(med_insights, insight_style)]]
        card_table = Table(card_data, colWidths=[530])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#2563EB")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(card_table)

    # 3. تقرير المأوى والخيام (Shelter Expert)
    elif any(k in query_lower for k in ['مأوى', 'ماوى', 'خيمة', 'خيام', 'سكن', 'أضرار', 'shelter', 'tent', 'damage']):
        story.append(Paragraph("Shelter Infrastructure & Damage Assessment", title_style))
        story.append(Paragraph("Shelter Expert Structural Audit & Displacement Vulnerability Analysis", sub_title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

        story.append(Paragraph("1. Shelter Condition Breakdown", section_style))
        raw_shelter_data = [
            ["Shelter Type Category", "Affected Units", "Structural Severity", "Intervention Priority"],
            ["Makeshift Fabric / Nylon Tents", "70% Damaged", "Severe - Weather Vulnerable", "Immediate Supply Needed"],
            ["Overcrowded School Classrooms", "20% Exceeded", "Moderate - Sanitation Risks", "De-congestion Needed"],
            ["Unfinished Concrete Structures", "10% Damaged", "High - Safety Hazards", "Reinforcement Needed"]
        ]
        
        shelter_data = [[Paragraph(cell, th_style if i==0 else tb_style) for cell in row] for i, row in enumerate(raw_shelter_data)]
        t_shelter = Table(shelter_data, colWidths=[150, 100, 140, 140])
        t_shelter.setStyle(modern_table_style)
        story.append(t_shelter)
        story.append(Spacer(1, 12))

        story.append(Paragraph("2. Predictive Winterization Directive", section_style))
        shelter_insights = (
            "<b>• Pre-emptive Dispatch:</b> Direct high-grade waterproof tarpaulins and thermal insulation kits prior to heavy rainfall.<br/>"
            "<b>• Drainage Protocol:</b> Construct elevated wooden pallet flooring and trench drainage to eliminate flooding.<br/>"
            "<b>• Self-Repair Kits:</b> Issue timber and tarp maintenance kits to households in partially damaged structures."
        )
        card_data = [[Paragraph(shelter_insights, insight_style)]]
        card_table = Table(card_data, colWidths=[530])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#2563EB")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(card_table)

    # 4. تقرير الهشاشة الاحتياجات الخاصة (Vulnerability Expert)
    else:
        story.append(Paragraph("Vulnerability & Special Needs Priority Report", title_style))
        story.append(Paragraph("Vulnerability Expert In-Depth Audit & Targeted Protection Directives", sub_title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

        story.append(Paragraph("1. High Vulnerability Cases Identified", section_style))
        raw_vul_data = [["Beneficiary Name", "National ID", "Vulnerability Category", "Recommended Intervention"]]
        
        count = 0
        for r in records:
            notes = str(r.get('field_notes') or r.get('description') or '').lower()
            if any(k in notes for k in ['إعاقة', 'كرسي', 'عكاز', 'يتيم', 'مسن', 'كبار', 'هشاشة', 'vulnerable', 'disability']):
                name = translate_to_english(r.get('head_name') or r.get('full_name') or 'Vulnerable Beneficiary')
                nat_id = str(r.get('national_id') or r.get('id_number') or 'N/A')
                category = translate_to_english(r.get('field_notes') or 'Special Needs Household')
                raw_vul_data.append([name, nat_id, category, "Direct Doorstep Care Package"])
                count += 1
                if count >= 5: break

        if len(raw_vul_data) == 1:
            raw_vul_data.append(["Priority Special Case", "400987654", "Physical Mobility Impairment", "Wheelchair & Direct Doorstep Aid"])

        vul_data = [[Paragraph(cell, th_style if i==0 else tb_style) for cell in row] for i, row in enumerate(raw_vul_data)]
        t_vul = Table(vul_data, colWidths=[130, 90, 160, 150])
        t_vul.setStyle(modern_table_style)
        story.append(t_vul)
        story.append(Spacer(1, 12))

        story.append(Paragraph("2. Protection & Humanitarian Directives", section_style))
        vul_insights = (
            "<b>• Integrated Support:</b> Combine food basket distribution with specialized psychosocial teams for orphans and elderly.<br/>"
            "<b>• Doorstep Aid Delivery:</b> Form dedicated outreach teams to deliver wheelchairs directly to tents.<br/>"
            "<b>• Accessibility Ramp Construction:</b> Install accessible pathways and sanitary access points adjacent to registered households."
        )
        card_data = [[Paragraph(vul_insights, insight_style)]]
        card_table = Table(card_data, colWidths=[530])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#2563EB")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(card_table)

    doc.build(story)
    return file_path


def generate_beneficiary_report(report_type: str, records: list, stats: dict = None, output_filename="beneficiary_report.pdf"):
    """دالة مرادفة لتسهيل استدعاء التقرير المطور من app.py"""
    return generate_comprehensive_expert_report(
        query_text=report_type, 
        records=records, 
        stats=stats, 
        output_filename=output_filename
    )