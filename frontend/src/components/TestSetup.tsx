import { useState } from "react";
import { api } from "../api";
import { useToast } from "../useToast";
import type { Level, LevelSummary, Mode, Test } from "../types";

interface Props {
  levels: LevelSummary[];
  openaiConfigured: boolean;
  onCancel: () => void;
  onCreated: (t: Test) => void;
}

const LEVEL_HELP: Record<Level, string> = {
  beginner: "Greetings, numbers, family, everyday items.",
  intermediate: "Workplace, travel, weather, common verbs & adjectives.",
  advanced: "Business, society, technology, abstract nouns.",
};

const MODE_HELP: Record<Mode, string> = {
  written: "Text-only translation questions (multiple choice + free text).",
  listening: "Hear the Korean word, answer in English.",
  mixed: "A blend of written and listening questions.",
};

const COUNTS = [5, 10, 20] as const;

export default function TestSetup({
  levels,
  openaiConfigured,
  onCancel,
  onCreated,
}: Props) {
  const [level, setLevel] = useState<Level>("beginner");
  const [mode, setMode] = useState<Mode>("written");
  const [numQuestions, setNumQuestions] = useState<number>(10);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

  const listeningDisabled = !openaiConfigured;

  async function handleCreate() {
    setSubmitting(true);
    setError(null);
    try {
      const t = await api.createTest({
        level,
        mode,
        num_questions: numQuestions,
      });
      onCreated(t);
    } catch (e) {
      const msg = (e as Error).message;
      setError(msg);
      showToast({
        kind: "error",
        title: "Could not create test",
        message: msg,
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">New test</h2>
        <p className="mt-1 text-sm text-slate-600">
          Configure your practice session.
        </p>
      </div>

      <fieldset>
        <legend className="text-sm font-medium text-slate-800">
          Experience level
        </legend>
        <div className="mt-2 grid grid-cols-3 gap-2">
          {(["beginner", "intermediate", "advanced"] as Level[]).map((l) => {
            const ls = levels.find((x) => x.level === l);
            return (
              <button
                key={l}
                type="button"
                onClick={() => setLevel(l)}
                className={
                  "rounded-lg border px-3 py-3 text-left text-sm transition " +
                  (level === l
                    ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200"
                    : "border-slate-200 bg-white hover:border-slate-300")
                }
              >
                <div className="font-medium capitalize text-slate-900">{l}</div>
                <div className="mt-1 text-xs text-slate-500">
                  {ls?.word_count ?? 0} words
                </div>
              </button>
            );
          })}
        </div>
        <p className="mt-2 text-xs text-slate-500">{LEVEL_HELP[level]}</p>
      </fieldset>

      <fieldset>
        <legend className="text-sm font-medium text-slate-800">Mode</legend>
        <div className="mt-2 grid grid-cols-3 gap-2">
          {(["written", "listening", "mixed"] as Mode[]).map((m) => {
            const isListening = m === "listening" || m === "mixed";
            const disabled = isListening && listeningDisabled && m === "listening";
            return (
              <button
                key={m}
                type="button"
                disabled={disabled}
                onClick={() => setMode(m)}
                className={
                  "rounded-lg border px-3 py-3 text-left text-sm transition " +
                  (mode === m
                    ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200"
                    : "border-slate-200 bg-white hover:border-slate-300") +
                  (disabled ? " cursor-not-allowed opacity-50" : "")
                }
              >
                <div className="font-medium capitalize text-slate-900">{m}</div>
                <div className="mt-1 text-xs text-slate-500">
                  {MODE_HELP[m]}
                </div>
              </button>
            );
          })}
        </div>
        {(mode === "mixed" || mode === "listening") && listeningDisabled && (
          <p className="mt-2 text-xs text-amber-700">
            {mode === "listening"
              ? "Listening mode is disabled without an OpenAI API key."
              : "Mixed mode will request audio; listening questions will fail until OPENAI_API_KEY is set."}
          </p>
        )}
      </fieldset>

      <fieldset>
        <legend className="text-sm font-medium text-slate-800">
          Number of questions
        </legend>
        <div className="mt-2 flex gap-2">
          {COUNTS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setNumQuestions(c)}
              className={
                "flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition " +
                (numQuestions === c
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700 ring-2 ring-indigo-200"
                  : "border-slate-200 bg-white text-slate-700 hover:border-slate-300")
              }
            >
              {c}
            </button>
          ))}
        </div>
      </fieldset>

      {error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
          {error}
        </div>
      )}

      <div className="flex justify-between gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-slate-300"
        >
          Cancel
        </button>
        <button
          type="button"
          disabled={submitting}
          onClick={handleCreate}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Generating…" : "Start test"}
        </button>
      </div>
    </div>
  );
}
