import type {
  Health,
  LevelSummary,
  Level,
  Mode,
  Test,
  TestSummary,
} from "./types";

// All frontend requests go to /api/* which the Vite dev proxy forwards
// to the FastAPI backend on localhost:8000. In a standalone deployment
// you can put a reverse proxy at /api/ or set VITE_API_BASE_URL.
const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  // DELETE returns JSON but with just {deleted}; we handle it uniformly.
  return (await res.json()) as T;
}

export const api = {
  healthz: () => request<Health>("/healthz"),
  listLevels: () => request<LevelSummary[]>("/vocab/levels"),
  createTest: (args: {
    level: Level;
    mode: Mode;
    num_questions: number;
    use_openai_vocab?: boolean;
  }) =>
    request<Test>("/tests", {
      method: "POST",
      body: JSON.stringify(args),
    }),
  listTests: () => request<TestSummary[]>("/tests"),
  getTest: (id: number) => request<Test>(`/tests/${id}`),
  submitTest: (id: number, answers: { question_id: number; answer: string }[]) =>
    request<Test>(`/tests/${id}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
  deleteTest: (id: number) =>
    request<{ deleted: number }>(`/tests/${id}`, { method: "DELETE" }),
  ttsUrl: (text: string) =>
    `${API_BASE}/tts?text=${encodeURIComponent(text)}`,
};
