from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChoiceSectionConfig(BaseModel):
    type: Literal["choice"]
    title: NonEmptyString
    questionCount: int = Field(gt=0)
    optionCount: int = Field(ge=2)
    options: list[NonEmptyString]
    questionsPerRow: int = Field(gt=0)
    questionsPerColumn: int = Field(gt=0)
    fillOrder: Literal["row_first", "column_first"]

    @model_validator(mode="after")
    def validate_options(self) -> "ChoiceSectionConfig":
        if len(self.options) != self.optionCount:
            raise ValueError("optionCount must equal options length")
        return self


class BlankSectionConfig(BaseModel):
    type: Literal["blank"]
    title: NonEmptyString
    questionCount: int = Field(gt=0)
    linesPerQuestion: int = Field(gt=0)


class CalculationSectionConfig(BaseModel):
    type: Literal["calculation"]
    title: NonEmptyString
    questionCount: int = Field(gt=0)
    heightPerQuestion: float = Field(gt=0)


SectionConfig = Union[ChoiceSectionConfig, BlankSectionConfig, CalculationSectionConfig]


class PaperConfig(BaseModel):
    paperTitle: NonEmptyString
    examName: str = ""
    pageSize: Literal["A4"]
    studentFields: list[NonEmptyString] = Field(min_length=1)
    showPositionMarks: bool = True
    sections: list[SectionConfig] = Field(min_length=1)

    @field_validator("sections", mode="before")
    @classmethod
    def parse_sections(cls, value):
        if not isinstance(value, list):
            return value

        parsed_sections = []
        for item in value:
            if not isinstance(item, dict):
                parsed_sections.append(item)
                continue

            section_type = item.get("type")
            if section_type == "choice":
                parsed_sections.append(ChoiceSectionConfig.model_validate(item))
            elif section_type == "blank":
                parsed_sections.append(BlankSectionConfig.model_validate(item))
            elif section_type == "calculation":
                parsed_sections.append(CalculationSectionConfig.model_validate(item))
            else:
                parsed_sections.append(item)

        return parsed_sections
