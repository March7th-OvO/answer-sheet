from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChoiceSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["choice"]
    title: NonEmptyString
    question_count: int = Field(validation_alias="questionCount", serialization_alias="questionCount", gt=0)
    option_count: int = Field(validation_alias="optionCount", serialization_alias="optionCount", ge=2)
    options: list[NonEmptyString]
    questions_per_row: int = Field(
        validation_alias="questionsPerRow",
        serialization_alias="questionsPerRow",
        gt=0,
    )
    questions_per_column: int = Field(
        validation_alias="questionsPerColumn",
        serialization_alias="questionsPerColumn",
        gt=0,
    )
    fill_order: Literal["row_first", "column_first"] = Field(
        validation_alias="fillOrder",
        serialization_alias="fillOrder",
    )

    @model_validator(mode="after")
    def validate_options(self) -> "ChoiceSectionConfig":
        if len(self.options) != self.option_count:
            raise ValueError("optionCount must equal options length")
        return self


class BlankSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["blank"]
    title: NonEmptyString
    question_count: int = Field(validation_alias="questionCount", serialization_alias="questionCount", gt=0)
    lines_per_question: int = Field(
        validation_alias="linesPerQuestion",
        serialization_alias="linesPerQuestion",
        gt=0,
    )


class CalculationSectionConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["calculation"]
    title: NonEmptyString
    question_count: int = Field(validation_alias="questionCount", serialization_alias="questionCount", gt=0)
    height_per_question: float = Field(
        validation_alias="heightPerQuestion",
        serialization_alias="heightPerQuestion",
        gt=0,
    )


SectionConfig = Annotated[
    Union[ChoiceSectionConfig, BlankSectionConfig, CalculationSectionConfig],
    Field(discriminator="type"),
]


class PaperConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    paper_title: NonEmptyString = Field(validation_alias="paperTitle", serialization_alias="paperTitle")
    exam_name: str = Field(validation_alias="examName", serialization_alias="examName", default="")
    page_size: Literal["A4"] = Field(validation_alias="pageSize", serialization_alias="pageSize")
    student_fields: list[NonEmptyString] = Field(
        validation_alias="studentFields",
        serialization_alias="studentFields",
        min_length=1,
    )
    show_position_marks: bool = Field(
        validation_alias="showPositionMarks",
        serialization_alias="showPositionMarks",
        default=True,
    )
    sections: list[SectionConfig] = Field(min_length=1)
