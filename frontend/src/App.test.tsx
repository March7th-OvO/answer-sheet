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
