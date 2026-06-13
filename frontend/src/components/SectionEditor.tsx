import type { AnswerSheetSection } from "../types/answerSheet";

type SectionEditorProps = {
  section: AnswerSheetSection;
};

export function SectionEditor({ section }: SectionEditorProps) {
  if (section.type === "choice") {
    return (
      <article className="section-card">
        <h3>{section.title}</h3>
        <p>
          选择题 {section.questionCount} 题 / {section.optionCount} 个选项 / {section.fillOrder}
        </p>
      </article>
    );
  }

  if (section.type === "blank") {
    return (
      <article className="section-card">
        <h3>{section.title}</h3>
        <p>
          填空题 {section.questionCount} 题 / 每题 {section.linesPerQuestion} 行
        </p>
      </article>
    );
  }

  return (
    <article className="section-card">
      <h3>{section.title}</h3>
      <p>
        计算题 {section.questionCount} 题 / 每题高度 {section.heightPerQuestion}mm
      </p>
    </article>
  );
}
