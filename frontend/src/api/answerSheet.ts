import axios from "axios";

import type { AnswerSheetPayload, GenerateFailure, GenerateSuccess } from "../types/answerSheet";

const client = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function generateAnswerSheet(
  payload: AnswerSheetPayload,
): Promise<GenerateSuccess | GenerateFailure> {
  const response = await client.post<GenerateSuccess | GenerateFailure>("/api/answer-sheet/generate", payload);
  return response.data;
}
