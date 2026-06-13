from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.core.constants import A4_WIDTH_MM, CONTENT_LEFT_MM, CONTENT_RIGHT_MM
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
    draw_header(pdf, layout.paper_title, exam_name, student_fields, active_font)

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
        if question.x is not None and question.y is not None:
            pdf.drawString(to_pt(question.x), to_pt(question.y - 1.5), f"{question.question_no}.")
        for option in question.options:
            pdf.circle(to_pt(option.x), to_pt(option.y), to_pt(option.radius))
            pdf.drawString(to_pt(option.x + 2.5), to_pt(option.y - 1.5), option.option)
        return

    if question.x is not None and question.y is not None and question.width and question.height:
        pdf.drawString(to_pt(question.x), to_pt(question.y + question.height + 1), f"{question.question_no}.")
        if question.type == "blank":
            draw_blank_answer_lines(pdf, question)
            return

        pdf.rect(to_pt(question.x), to_pt(question.y), to_pt(question.width), to_pt(question.height))


def draw_header(
    pdf: canvas.Canvas,
    paper_title: str,
    exam_name: str,
    student_fields: list[str],
    font_name: str,
) -> None:
    center_x = A4_WIDTH_MM / 2

    pdf.setFont(font_name, 16)
    pdf.drawCentredString(to_pt(center_x), to_pt(276), paper_title)
    if exam_name:
        pdf.setFont(font_name, 11)
        pdf.drawCentredString(to_pt(center_x), to_pt(268), exam_name)

    pdf.setFont(font_name, 10)
    student_text = format_student_fields(student_fields)
    pdf.drawString(to_pt(CONTENT_LEFT_MM), to_pt(254), student_text)


def draw_blank_answer_lines(pdf: canvas.Canvas, question: QuestionLayout) -> None:
    line_count = max(question.line_count, 1)
    line_gap = (question.height or 0) / line_count
    line_end_x = (question.x or CONTENT_LEFT_MM) + (question.width or (CONTENT_RIGHT_MM - CONTENT_LEFT_MM))
    line_start_x = (question.x or CONTENT_LEFT_MM) + 10

    for index in range(line_count):
        line_y = (question.y or 0) + (question.height or 0) - ((index + 1) * line_gap) + 1
        pdf.line(to_pt(line_start_x), to_pt(line_y), to_pt(line_end_x), to_pt(line_y))


def format_student_fields(student_fields: list[str]) -> str:
    return "    ".join(f"{field}：__________" for field in student_fields)


def to_pt(value_mm: float) -> float:
    return value_mm * mm


def collect_section_titles(layout: LayoutDocument) -> list[str]:
    return [section.title for section in layout.page.sections]
