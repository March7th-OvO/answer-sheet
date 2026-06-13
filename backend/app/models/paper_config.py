from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChoiceSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["choice"]
    title: NonEmptyString
    question_count: int = Field(alias="questionCount", gt=0)
    option_count: int = Field(alias="optionCount", ge=2)
    options: list[NonEmptyString]
    questions_per_row: int = Field(alias="questionsPerRow", gt=0)
    questions_per_column: int = Field(alias="questionsPerColumn", gt=0)
    fill_order: Literal["row_first", "column_first"] = Field(alias="fillOrder")

    @model_validator(mode="after")
    def validate_options(self) -> "ChoiceSectionConfig":
        if len(self.options) != self.option_count:
            raise ValueError("optionCount must equal options length")
        return self


class BlankSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["blank"]
    title: NonEmptyString
    question_count: int = Field(alias="questionCount", gt=0)
    lines_per_question: int = Field(alias="linesPerQuestion", gt=0)


class CalculationSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["calculation"]
    title: NonEmptyString
    question_count: int = Field(alias="questionCount", gt=0)
    height_per_question: float = Field(alias="heightPerQuestion", gt=0)


SectionConfig = Annotated[
    Union[ChoiceSectionConfig, BlankSectionConfig, CalculationSectionConfig],
    Field(discriminator="type"),
]


class PaperConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    paper_title: Annotated[NonEmptyString, Field(alias="paperTitle")]
    exam_name: Annotated[str, Field(alias="examName")] = ""
    page_size: Annotated[Literal["A4"], Field(alias="pageSize")]
    student_fields: Annotated[list[NonEmptyString], Field(alias="studentFields", min_length=1)]
    show_position_marks: Annotated[bool, Field(alias="showPositionMarks")] = True
    sections: Annotated[list[SectionConfig], Field(min_length=1)]
