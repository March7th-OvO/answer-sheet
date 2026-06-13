export type FillOrder = "row_first" | "column_first";

export type ChoiceSection = {
  type: "choice";
  title: string;
  questionCount: number;
  optionCount: number;
  options: string[];
  questionsPerRow: number;
  questionsPerColumn: number;
  fillOrder: FillOrder;
};

export type BlankSection = {
  type: "blank";
  title: string;
  questionCount: number;
  linesPerQuestion: number;
};

export type CalculationSection = {
  type: "calculation";
  title: string;
  questionCount: number;
  heightPerQuestion: number;
};

export type AnswerSheetSection = ChoiceSection | BlankSection | CalculationSection;

export type AnswerSheetPayload = {
  paperTitle: string;
  examName: string;
  pageSize: "A4";
  studentFields: string[];
  showPositionMarks: boolean;
  sections: AnswerSheetSection[];
};

export type GenerateSuccess = {
  success: true;
  taskId: string;
  pdfUrl: string;
  layoutJsonUrl: string;
  message: string;
};

export type GenerateFailure = {
  success: false;
  errorCode: string;
  message: string;
};
