import { useEffect, useState } from "react";

import type { AnswerSheetSection, FillOrder } from "../types/answerSheet";

type SectionEditorProps = {
  section: AnswerSheetSection;
  onChange: (section: AnswerSheetSection) => void;
  onRemove: () => void;
};

export function SectionEditor({ section, onChange, onRemove }: SectionEditorProps) {
  if (section.type === "choice") {
    return (
      <ChoiceSectionEditor section={section} onChange={onChange} onRemove={onRemove} />
    );
  }

  if (section.type === "blank") {
    return (
      <article className="section-card">
        <div className="section-card-header">
          <h3>{section.title}</h3>
          <button type="button" className="ghost-button" onClick={onRemove}>
            删除分区
          </button>
        </div>
        <label>
          <span>填空题标题</span>
          <input value={section.title} onChange={(event) => onChange({ ...section, title: event.target.value })} />
        </label>
        <div className="section-field-grid">
          <label>
            <span>填空题数量</span>
            <input
              type="number"
              min={1}
              value={section.questionCount}
              onChange={(event) => onChange({ ...section, questionCount: Number(event.target.value) })}
            />
          </label>
          <label>
            <span>每题横线数</span>
            <input
              type="number"
              min={1}
              value={section.linesPerQuestion}
              onChange={(event) => onChange({ ...section, linesPerQuestion: Number(event.target.value) })}
            />
          </label>
        </div>
      </article>
    );
  }

  return (
    <article className="section-card">
      <div className="section-card-header">
        <h3>{section.title}</h3>
        <button type="button" className="ghost-button" onClick={onRemove}>
          删除分区
        </button>
      </div>
      <label>
        <span>计算题标题</span>
        <input value={section.title} onChange={(event) => onChange({ ...section, title: event.target.value })} />
      </label>
      <div className="section-field-grid">
        <label>
          <span>计算题数量</span>
          <input
            type="number"
            min={1}
            value={section.questionCount}
            onChange={(event) => onChange({ ...section, questionCount: Number(event.target.value) })}
          />
        </label>
        <label>
          <span>每题高度（mm）</span>
          <input
            type="number"
            min={1}
            value={section.heightPerQuestion}
            onChange={(event) => onChange({ ...section, heightPerQuestion: Number(event.target.value) })}
          />
        </label>
      </div>
    </article>
  );
}

function ChoiceSectionEditor({
  section,
  onChange,
  onRemove,
}: {
  section: Extract<AnswerSheetSection, { type: "choice" }>;
  onChange: (section: AnswerSheetSection) => void;
  onRemove: () => void;
}) {
  const [optionsText, setOptionsText] = useState(section.options.join(","));

  useEffect(() => {
    setOptionsText(section.options.join(","));
  }, [section.options]);

  const commitOptions = () => {
    const options = parseOptions(optionsText);
    onChange({
      ...section,
      options,
      optionCount: options.length,
    });
  };

  return (
    <article className="section-card">
      <div className="section-card-header">
        <h3>{section.title}</h3>
        <button type="button" className="ghost-button" onClick={onRemove}>
          删除分区
        </button>
      </div>
      <label>
        <span>选择题标题</span>
        <input value={section.title} onChange={(event) => onChange({ ...section, title: event.target.value })} />
      </label>
      <div className="section-field-grid">
        <label>
          <span>选择题数量</span>
          <input
            type="number"
            min={1}
            value={section.questionCount}
            onChange={(event) => onChange({ ...section, questionCount: Number(event.target.value) })}
          />
        </label>
        <label>
          <span>选项数量</span>
          <input
            type="number"
            min={2}
            value={section.optionCount}
            onChange={(event) => onChange(syncChoiceOptions(section, Number(event.target.value)))}
          />
        </label>
        <label>
          <span>每行题目数</span>
          <input
            type="number"
            min={1}
            value={section.questionsPerRow}
            onChange={(event) => onChange({ ...section, questionsPerRow: Number(event.target.value) })}
          />
        </label>
        <label>
          <span>每列题目数</span>
          <input
            type="number"
            min={1}
            value={section.questionsPerColumn}
            onChange={(event) => onChange({ ...section, questionsPerColumn: Number(event.target.value) })}
          />
        </label>
      </div>
      <label>
        <span>选择题选项</span>
        <input value={optionsText} onChange={(event) => setOptionsText(event.target.value)} onBlur={commitOptions} />
      </label>
      <label>
        <span>排列方式</span>
        <select
          value={section.fillOrder}
          onChange={(event) =>
            onChange({
              ...section,
              fillOrder: event.target.value as FillOrder,
            })
          }
        >
          <option value="column_first">column_first</option>
          <option value="row_first">row_first</option>
        </select>
      </label>
    </article>
  );
}

function parseOptions(value: string): string[] {
  return value
    .split(",")
    .map((option) => option.trim())
    .filter(Boolean);
}

function syncChoiceOptions(section: Extract<AnswerSheetSection, { type: "choice" }>, optionCount: number) {
  const safeCount = Math.max(2, optionCount || 0);
  const options = Array.from({ length: safeCount }, (_, index) => section.options[index] ?? String.fromCharCode(65 + index));
  return {
    ...section,
    optionCount: safeCount,
    options,
  };
}
