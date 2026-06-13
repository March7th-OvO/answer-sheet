from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.core.constants import CONTENT_LEFT_MM
from app.services.font_service import ensure_font
from app.services.layout_engine import LayoutDocument, QuestionLayout


def render_pdf(
    layout: LayoutDocument,
    exam_name: str,
    student_fields: list[str],
    font_path: Path | None = None,
    font_name: str | None = None,
) -> bytes:
    active_font = ensure_font(
        font_path=font_path,
        font_name=font_name,
        text_samples=[layout.paper_title, exam_name, *student_fields, *collect_section_titles(layout)],
    )
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(layout.paper_title)
    pdf.setFont(active_font, 14)
    pdf.drawString(to_pt(CONTENT_LEFT_MM), to_pt(280), layout.paper_title)
    pdf.setFont(active_font, 10)
    if exam_name:
        pdf.drawString(to_pt(CONTENT_LEFT_MM), to_pt(272), exam_name)
    pdf.drawString(to_pt(CONTENT_LEFT_MM), to_pt(262), " / ".join(student_fields))

    for mark in layout.page.position_marks:
        pdf.rect(to_pt(mark.x), to_pt(mark.y), to_pt(mark.width), to_pt(mark.height))

    for section in layout.page.sections:
        pdf.setFont(active_font, 11)
        pdf.drawString(to_pt(section.x), to_pt(section.y + section.height - 6), section.title)
        for question in section.questions:
            draw_question(pdf, question, active_font)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def draw_question(pdf: canvas.Canvas, question: QuestionLayout, font_name: str) -> None:
    pdf.setFont(font_name, 10)
    if question.options:
        for option in question.options:
            pdf.circle(to_pt(option.x), to_pt(option.y), to_pt(option.radius))
            pdf.drawString(to_pt(option.x - 1.5), to_pt(option.y + 2.5), option.option)
        return

    if question.x is not None and question.y is not None and question.width and question.height:
        pdf.drawString(to_pt(question.x), to_pt(question.y + question.height + 1), f"{question.question_no}.")
        pdf.rect(to_pt(question.x), to_pt(question.y), to_pt(question.width), to_pt(question.height))


def to_pt(value_mm: float) -> float:
    return value_mm * mm


def collect_section_titles(layout: LayoutDocument) -> list[str]:
    return [section.title for section in layout.page.sections]
