import { useState } from "react";

import { generateAnswerSheet } from "./api/answerSheet";
import { BasicInfoForm } from "./components/BasicInfoForm";
import { ResultPanel } from "./components/ResultPanel";
import { SectionList } from "./components/SectionList";
import "./styles.css";
import type { AnswerSheetPayload, AnswerSheetSection } from "./types/answerSheet";

const DEFAULT_SECTIONS: AnswerSheetSection[] = [
  createDefaultSection("choice", "一、选择题"),
  createDefaultSection("blank", "二、填空题"),
  createDefaultSection("calculation", "三、计算题"),
];

function App() {
  const [paperTitle, setPaperTitle] = useState("答题卡");
  const [examName, setExamName] = useState("");
  const [showPositionMarks, setShowPositionMarks] = useState(true);
  const [studentFieldsText, setStudentFieldsText] = useState("姓名,学号,班级");
  const [sections, setSections] = useState<AnswerSheetSection[]>(DEFAULT_SECTIONS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");
  const [layoutJsonUrl, setLayoutJsonUrl] = useState("");

  const handleFieldChange = (
    field: "paperTitle" | "examName" | "showPositionMarks" | "studentFieldsText",
    value: string | boolean,
  ) => {
    if (field === "paperTitle") setPaperTitle(value as string);
    if (field === "examName") setExamName(value as string);
    if (field === "showPositionMarks") setShowPositionMarks(value as boolean);
    if (field === "studentFieldsText") setStudentFieldsText(value as string);
  };

  const handleSectionChange = (index: number, section: AnswerSheetSection) => {
    setSections((currentSections) =>
      currentSections.map((currentSection, currentIndex) => (currentIndex === index ? section : currentSection)),
    );
  };

  const handleSectionRemove = (index: number) => {
    setSections((currentSections) => currentSections.filter((_, currentIndex) => currentIndex !== index));
  };

  const handleSectionAdd = (type: AnswerSheetSection["type"]) => {
    const titlePrefix = getSectionTitlePrefix(type);
    const sectionCount = sections.filter((section) => section.type === type).length;
    setSections((currentSections) => [
      ...currentSections,
      createDefaultSection(type, `${titlePrefix}${sectionCount + 1}`),
    ]);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setPdfUrl("");
    setLayoutJsonUrl("");

    const payload: AnswerSheetPayload = {
      paperTitle,
      examName,
      pageSize: "A4",
      studentFields: studentFieldsText
        .split(",")
        .map((field) => field.trim())
        .filter(Boolean),
      showPositionMarks,
      sections,
    };

    try {
      const result = await generateAnswerSheet(payload);
      if (result.success) {
        setPdfUrl(`http://127.0.0.1:8000${result.pdfUrl}`);
        setLayoutJsonUrl(`http://127.0.0.1:8000${result.layoutJsonUrl}`);
      } else {
        setError(result.message);
      }
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "生成失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">A4 Single Page</p>
        <h1>答题卡生成器</h1>
        <p>先打通从配置输入到 PDF 与 layout.json 导出的最小闭环。</p>
      </section>
      <div className="content-grid">
        <BasicInfoForm
          examName={examName}
          paperTitle={paperTitle}
          showPositionMarks={showPositionMarks}
          studentFieldsText={studentFieldsText}
          onFieldChange={handleFieldChange}
        />
        <SectionList
          sections={sections}
          onSectionChange={handleSectionChange}
          onSectionRemove={handleSectionRemove}
          onSectionAdd={handleSectionAdd}
        />
        <section className="panel action-panel">
          <h2>生成操作</h2>
          <button type="button" onClick={handleSubmit} disabled={loading}>
            生成答题卡
          </button>
        </section>
        <ResultPanel loading={loading} error={error} pdfUrl={pdfUrl} layoutJsonUrl={layoutJsonUrl} />
      </div>
    </main>
  );
}

export default App;

function createDefaultSection(type: AnswerSheetSection["type"], title: string): AnswerSheetSection {
  if (type === "choice") {
    return {
      type,
      title,
      questionCount: 20,
      optionCount: 4,
      options: ["A", "B", "C", "D"],
      questionsPerRow: 4,
      questionsPerColumn: 5,
      fillOrder: "column_first",
    };
  }

  if (type === "blank") {
    return {
      type,
      title,
      questionCount: 3,
      linesPerQuestion: 1,
    };
  }

  return {
    type,
    title,
    questionCount: 2,
    heightPerQuestion: 25,
  };
}

function getSectionTitlePrefix(type: AnswerSheetSection["type"]): string {
  if (type === "choice") return "选择题";
  if (type === "blank") return "填空题";
  return "计算题";
}
