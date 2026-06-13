import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";

import { generateAnswerSheet } from "./api/answerSheet";
import App from "./App";

vi.mock("./api/answerSheet", () => ({
  generateAnswerSheet: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

test("renders default form sections and generate action", () => {
  render(<App />);

  expect(screen.getByText("答题卡生成器")).toBeInTheDocument();
  expect(screen.getByLabelText("答题卡标题")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "生成答题卡" })).toBeInTheDocument();
  expect(screen.getByText("结果下载")).toBeInTheDocument();
});

test("shows download links after successful submission", async () => {
  vi.mocked(generateAnswerSheet).mockResolvedValue({
    success: true,
    taskId: "sheet_001",
    pdfUrl: "/api/files/sheet_001.pdf",
    layoutJsonUrl: "/api/files/sheet_001_layout.json",
    message: "ok",
  });

  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("button", { name: "生成答题卡" }));

  await waitFor(() => {
    expect(screen.getByRole("link", { name: "下载 PDF" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "下载 layout.json" })).toBeInTheDocument();
  });
});

test("shows backend message after failed submission", async () => {
  vi.mocked(generateAnswerSheet).mockResolvedValue({
    success: false,
    errorCode: "PAGE_HEIGHT_EXCEEDED",
    message: "答题卡内容超出 A4 单页可用高度",
  });

  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("button", { name: "生成答题卡" }));

  await waitFor(() => {
    expect(screen.getByText("答题卡内容超出 A4 单页可用高度")).toBeInTheDocument();
  });
});

test("submits edited sections from the form", async () => {
  vi.mocked(generateAnswerSheet).mockResolvedValue({
    success: true,
    taskId: "sheet_001",
    pdfUrl: "/api/files/sheet_001.pdf",
    layoutJsonUrl: "/api/files/sheet_001_layout.json",
    message: "ok",
  });

  const user = userEvent.setup();
  render(<App />);

  await user.clear(screen.getByLabelText("答题卡标题"));
  await user.type(screen.getByLabelText("答题卡标题"), "软件工程期末考试答题卡");
  await user.clear(screen.getByLabelText("学生字段"));
  await user.type(screen.getByLabelText("学生字段"), "姓名,学号");
  await user.clear(screen.getByLabelText("选择题数量"));
  await user.type(screen.getByLabelText("选择题数量"), "30");
  await user.clear(screen.getByLabelText("选择题选项"));
  await user.type(screen.getByLabelText("选择题选项"), "A,B,C,D,E");
  await user.clear(screen.getByLabelText("每行题目数"));
  await user.type(screen.getByLabelText("每行题目数"), "3");
  await user.selectOptions(screen.getByLabelText("排列方式"), "row_first");
  await user.click(screen.getByRole("button", { name: "添加计算题" }));
  await user.clear(screen.getAllByLabelText("计算题标题")[1]);
  await user.type(screen.getAllByLabelText("计算题标题")[1], "四、附加题");
  await user.clear(screen.getAllByLabelText("每题高度（mm）")[1]);
  await user.type(screen.getAllByLabelText("每题高度（mm）")[1], "40");
  await user.click(screen.getAllByRole("button", { name: "删除分区" })[1]);
  await user.click(screen.getByRole("button", { name: "生成答题卡" }));

  await waitFor(() => {
    expect(generateAnswerSheet).toHaveBeenCalledWith({
      paperTitle: "软件工程期末考试答题卡",
      examName: "",
      pageSize: "A4",
      studentFields: ["姓名", "学号"],
      showPositionMarks: true,
      sections: [
        {
          type: "choice",
          title: "一、选择题",
          questionCount: 30,
          optionCount: 5,
          options: ["A", "B", "C", "D", "E"],
          questionsPerRow: 3,
          questionsPerColumn: 5,
          fillOrder: "row_first",
        },
        {
          type: "calculation",
          title: "三、计算题",
          questionCount: 2,
          heightPerQuestion: 25,
        },
        {
          type: "calculation",
          title: "四、附加题",
          questionCount: 2,
          heightPerQuestion: 40,
        },
      ],
    });
  });
});
