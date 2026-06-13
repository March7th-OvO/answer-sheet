import type { AnswerSheetSection } from "../types/answerSheet";
import { SectionEditor } from "./SectionEditor";

type SectionListProps = {
  sections: AnswerSheetSection[];
  onSectionChange: (index: number, section: AnswerSheetSection) => void;
  onSectionRemove: (index: number) => void;
  onSectionAdd: (type: AnswerSheetSection["type"]) => void;
};

export function SectionList({ sections, onSectionChange, onSectionRemove, onSectionAdd }: SectionListProps) {
  return (
    <section className="panel">
      <h2>题型配置</h2>
      <div className="section-list">
        {sections.map((section, index) => (
          <SectionEditor
            key={`${section.type}-${index}`}
            section={section}
            onChange={(nextSection) => onSectionChange(index, nextSection)}
            onRemove={() => onSectionRemove(index)}
          />
        ))}
      </div>
      <div className="section-actions">
        <button type="button" className="secondary-button" onClick={() => onSectionAdd("choice")}>
          添加选择题
        </button>
        <button type="button" className="secondary-button" onClick={() => onSectionAdd("blank")}>
          添加填空题
        </button>
        <button type="button" className="secondary-button" onClick={() => onSectionAdd("calculation")}>
          添加计算题
        </button>
      </div>
    </section>
  );
}
