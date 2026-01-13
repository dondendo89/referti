from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


def create_pdf(report_text: str, file_path: str) -> None:
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], alignment=TA_CENTER)
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=11, leading=16, alignment=TA_JUSTIFY)
    disclaimer_style = ParagraphStyle("Disclaimer", parent=styles["BodyText"], fontSize=8, leading=12, alignment=TA_JUSTIFY)
    story = []
    story.append(Paragraph("Referto Radiologico", title_style))
    story.append(Spacer(1, 12))
    for part in report_text.split("\n\n"):
        story.append(Paragraph(part.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 8))
    story.append(Spacer(1, 16))
    disclaimer = (
        "Questo referto è generato con supporto AI e non sostituisce il giudizio medico. "
        "Evitare l'uso di dati identificativi. Valutazione clinica finale a cura del medico responsabile."
    )
    story.append(Paragraph(disclaimer, disclaimer_style))
    doc.build(story)