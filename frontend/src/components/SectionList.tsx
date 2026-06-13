import type { AnswerSheetSection } from "../types/answerSheet";
import { SectionEditor } from "./SectionEditor";

type SectionListProps = {
  sections: AnswerSheetSection[];
};

export function SectionList({ sections }: SectionListProps) {
  return (
    <section className="panel">
      <h2>题型配置</h2>
      <div className="section-list">
        {sections.map((section, index) => (
          <SectionEditor key={`${section.type}-${index}`} section={section} />
        ))}
      </div>
    </section>
  );
}
