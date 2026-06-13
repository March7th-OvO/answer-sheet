import type { ChangeEvent } from "react";

type BasicInfoProps = {
  examName: string;
  paperTitle: string;
  showPositionMarks: boolean;
  studentFieldsText: string;
  onFieldChange: (field: "paperTitle" | "examName" | "showPositionMarks" | "studentFieldsText", value: string | boolean) => void;
};

export function BasicInfoForm({
  examName,
  paperTitle,
  showPositionMarks,
  studentFieldsText,
  onFieldChange,
}: BasicInfoProps) {
  const handleInputChange =
    (field: "paperTitle" | "examName" | "studentFieldsText") =>
    (event: ChangeEvent<HTMLInputElement>) => {
      onFieldChange(field, event.target.value);
    };

  return (
    <section className="panel">
      <h2>基础信息</h2>
      <label>
        <span>答题卡标题</span>
        <input value={paperTitle} onChange={handleInputChange("paperTitle")} />
      </label>
      <label>
        <span>考试名称</span>
        <input value={examName} onChange={handleInputChange("examName")} />
      </label>
      <label>
        <span>学生字段</span>
        <input value={studentFieldsText} onChange={handleInputChange("studentFieldsText")} />
      </label>
      <label className="checkbox">
        <input
          type="checkbox"
          checked={showPositionMarks}
          onChange={(event) => onFieldChange("showPositionMarks", event.target.checked)}
        />
        <span>显示四角定位点</span>
      </label>
    </section>
  );
}
