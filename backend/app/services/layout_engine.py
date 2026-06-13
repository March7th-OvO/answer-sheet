from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil

from app.core.constants import (
    A4_HEIGHT_MM,
    A4_WIDTH_MM,
    BLANK_LINE_HEIGHT_MM,
    BLANK_QUESTION_GAP_MM,
    BOTTOM_MARGIN_MM,
    CALCULATION_NUMBER_HEIGHT_MM,
    CALCULATION_QUESTION_GAP_MM,
    CHOICE_BUBBLE_RADIUS_MM,
    CHOICE_CELL_GAP_MM,
    CHOICE_NUMBER_WIDTH_MM,
    CHOICE_OPTION_SPACING_MM,
    CHOICE_ROW_HEIGHT_MM,
    CONTENT_LEFT_MM,
    CONTENT_RIGHT_MM,
    CONTENT_WIDTH_MM,
    HEADER_GAP_MM,
    HEADER_SECTION_GAP_MM,
    HEADER_TITLE_HEIGHT_MM,
    POSITION_MARK_OFFSET_MM,
    POSITION_MARK_SIZE_MM,
    SECTION_GAP_MM,
    SECTION_TITLE_HEIGHT_MM,
    STUDENT_INFO_HEIGHT_MM,
    TITLE_TO_CONTENT_GAP_MM,
    TOP_MARGIN_MM,
)
from app.core.errors import AppError
from app.models.paper_config import (
    BlankSectionConfig,
    CalculationSectionConfig,
    ChoiceSectionConfig,
    PaperConfig,
)


@dataclass(slots=True)
class ChoiceOptionLayout:
    option: str
    x: float
    y: float
    radius: float


@dataclass(slots=True)
class QuestionLayout:
    question_no: int
    type: str
    options: list[ChoiceOptionLayout] = field(default_factory=list)
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    line_count: int = 1


@dataclass(slots=True)
class SectionLayout:
    type: str
    title: str
    x: float
    y: float
    width: float
    height: float
    questions: list[QuestionLayout]


@dataclass(slots=True)
class PositionMarkLayout:
    name: str
    x: float
    y: float
    width: float
    height: float


@dataclass(slots=True)
class PageLayout:
    page_index: int
    width: float
    height: float
    position_marks: list[PositionMarkLayout]
    sections: list[SectionLayout]


@dataclass(slots=True)
class LayoutDocument:
    sheet_id: str
    paper_title: str
    page_size: str
    unit: str
    coordinate_system: str
    page: PageLayout


def build_layout(config: PaperConfig, sheet_id: str = "preview") -> LayoutDocument:
    position_marks = build_position_marks()
    current_top = TOP_MARGIN_MM + HEADER_TITLE_HEIGHT_MM + HEADER_GAP_MM + STUDENT_INFO_HEIGHT_MM + HEADER_SECTION_GAP_MM
    sections: list[SectionLayout] = []

    for index, section in enumerate(config.sections):
        has_more_sections = index < len(config.sections) - 1
        if isinstance(section, ChoiceSectionConfig):
            section_layout, consumed_height = build_choice_section(section, current_top)
        elif isinstance(section, BlankSectionConfig):
            section_layout, consumed_height = build_blank_section(section, current_top)
        else:
            section_layout, consumed_height = build_calculation_section(section, current_top)

        if current_top + consumed_height + BOTTOM_MARGIN_MM > A4_HEIGHT_MM:
            raise AppError(
                "PAGE_HEIGHT_EXCEEDED",
                "答题卡内容超出 A4 单页可用高度，请减少题量或调整排版参数",
            )

        sections.append(section_layout)
        current_top += consumed_height
        if has_more_sections:
            current_top += SECTION_GAP_MM

    page = PageLayout(
        page_index=1,
        width=A4_WIDTH_MM,
        height=A4_HEIGHT_MM,
        position_marks=position_marks,
        sections=sections,
    )

    return LayoutDocument(
        sheet_id=sheet_id,
        paper_title=config.paperTitle,
        page_size=config.pageSize,
        unit="mm",
        coordinate_system="pdf_bottom_left",
        page=page,
    )


def build_position_marks() -> list[PositionMarkLayout]:
    top_y = A4_HEIGHT_MM - POSITION_MARK_OFFSET_MM - POSITION_MARK_SIZE_MM
    bottom_y = POSITION_MARK_OFFSET_MM
    left_x = POSITION_MARK_OFFSET_MM
    right_x = A4_WIDTH_MM - POSITION_MARK_OFFSET_MM - POSITION_MARK_SIZE_MM
    return [
        PositionMarkLayout("top_left", left_x, top_y, POSITION_MARK_SIZE_MM, POSITION_MARK_SIZE_MM),
        PositionMarkLayout("top_right", right_x, top_y, POSITION_MARK_SIZE_MM, POSITION_MARK_SIZE_MM),
        PositionMarkLayout("bottom_left", left_x, bottom_y, POSITION_MARK_SIZE_MM, POSITION_MARK_SIZE_MM),
        PositionMarkLayout("bottom_right", right_x, bottom_y, POSITION_MARK_SIZE_MM, POSITION_MARK_SIZE_MM),
    ]


def build_choice_section(section: ChoiceSectionConfig, top_offset: float) -> tuple[SectionLayout, float]:
    capacity = section.questionsPerRow * section.questionsPerColumn
    if section.questionCount > capacity:
        raise AppError("CHOICE_GRID_CAPACITY_EXCEEDED", "选择题数量超过当前选择题网格容量")

    cell_width = CHOICE_NUMBER_WIDTH_MM + (section.optionCount * CHOICE_OPTION_SPACING_MM)
    total_width = (section.questionsPerRow * cell_width) + ((section.questionsPerRow - 1) * CHOICE_CELL_GAP_MM)
    if total_width > CONTENT_WIDTH_MM:
        raise AppError(
            "PAGE_WIDTH_EXCEEDED",
            "选择题区域超出 A4 单页可用宽度，请减少每行题目数量或减少选项数量",
        )

    used_rows = compute_used_choice_rows(section)
    section_height = SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM + (used_rows * CHOICE_ROW_HEIGHT_MM)
    section_y = page_y_from_top(top_offset + section_height)
    questions = build_choice_questions(section, top_offset + SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM, cell_width)

    return (
        SectionLayout(
            type=section.type,
            title=section.title,
            x=CONTENT_LEFT_MM,
            y=section_y,
            width=total_width,
            height=section_height,
            questions=questions,
        ),
        section_height,
    )


def build_blank_section(section: BlankSectionConfig, top_offset: float) -> tuple[SectionLayout, float]:
    content_height = (
        section.questionCount * section.linesPerQuestion * BLANK_LINE_HEIGHT_MM
        + (section.questionCount - 1) * BLANK_QUESTION_GAP_MM
    )
    section_height = SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM + content_height
    questions: list[QuestionLayout] = []
    question_top = top_offset + SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM

    for question_no in range(1, section.questionCount + 1):
        line_height = section.linesPerQuestion * BLANK_LINE_HEIGHT_MM
        y = page_y_from_top(question_top + line_height)
        questions.append(
            QuestionLayout(
                question_no=question_no,
                type=section.type,
                x=CONTENT_LEFT_MM,
                y=y,
                width=CONTENT_RIGHT_MM - CONTENT_LEFT_MM,
                height=line_height,
                line_count=section.linesPerQuestion,
            )
        )
        question_top += line_height + BLANK_QUESTION_GAP_MM

    return (
        SectionLayout(
            type=section.type,
            title=section.title,
            x=CONTENT_LEFT_MM,
            y=page_y_from_top(top_offset + section_height),
            width=CONTENT_RIGHT_MM - CONTENT_LEFT_MM,
            height=section_height,
            questions=questions,
        ),
        section_height,
    )


def build_calculation_section(section: CalculationSectionConfig, top_offset: float) -> tuple[SectionLayout, float]:
    question_block_height = CALCULATION_NUMBER_HEIGHT_MM + section.heightPerQuestion
    content_height = (section.questionCount * question_block_height) + (
        (section.questionCount - 1) * CALCULATION_QUESTION_GAP_MM
    )
    section_height = SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM + content_height
    questions: list[QuestionLayout] = []
    question_top = top_offset + SECTION_TITLE_HEIGHT_MM + TITLE_TO_CONTENT_GAP_MM

    for question_no in range(1, section.questionCount + 1):
        answer_top = question_top + CALCULATION_NUMBER_HEIGHT_MM
        questions.append(
            QuestionLayout(
                question_no=question_no,
                type=section.type,
                x=CONTENT_LEFT_MM,
                y=page_y_from_top(answer_top + section.heightPerQuestion),
                width=CONTENT_RIGHT_MM - CONTENT_LEFT_MM,
                height=section.heightPerQuestion,
            )
        )
        question_top += question_block_height + CALCULATION_QUESTION_GAP_MM

    return (
        SectionLayout(
            type=section.type,
            title=section.title,
            x=CONTENT_LEFT_MM,
            y=page_y_from_top(top_offset + section_height),
            width=CONTENT_RIGHT_MM - CONTENT_LEFT_MM,
            height=section_height,
            questions=questions,
        ),
        section_height,
    )


def build_choice_questions(
    section: ChoiceSectionConfig,
    content_top: float,
    cell_width: float,
) -> list[QuestionLayout]:
    questions: list[QuestionLayout] = []

    for question_no in range(1, section.questionCount + 1):
        row_index, column_index = compute_choice_position(question_no, section)
        center_y = page_y_from_top(content_top + (row_index * CHOICE_ROW_HEIGHT_MM) + (CHOICE_ROW_HEIGHT_MM / 2))
        base_x = CONTENT_LEFT_MM + (column_index * (cell_width + CHOICE_CELL_GAP_MM)) + CHOICE_NUMBER_WIDTH_MM + 4
        options = [
            ChoiceOptionLayout(
                option=option,
                x=base_x + (option_index * CHOICE_OPTION_SPACING_MM),
                y=center_y,
                radius=CHOICE_BUBBLE_RADIUS_MM,
            )
            for option_index, option in enumerate(section.options)
        ]
        questions.append(
            QuestionLayout(
                question_no=question_no,
                type=section.type,
                options=options,
                x=CONTENT_LEFT_MM + (column_index * (cell_width + CHOICE_CELL_GAP_MM)),
                y=center_y,
            )
        )

    return questions


def compute_choice_position(question_no: int, section: ChoiceSectionConfig) -> tuple[int, int]:
    index = question_no - 1
    if section.fillOrder == "column_first":
        row_index = index % section.questionsPerColumn
        column_index = index // section.questionsPerColumn
        return row_index, column_index

    row_index = index // section.questionsPerRow
    column_index = index % section.questionsPerRow
    return row_index, column_index


def compute_used_choice_rows(section: ChoiceSectionConfig) -> int:
    if section.fillOrder == "column_first":
        return min(section.questionsPerColumn, section.questionCount)
    return ceil(section.questionCount / section.questionsPerRow)


def page_y_from_top(top_value: float) -> float:
    return A4_HEIGHT_MM - top_value
