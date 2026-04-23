import { useMemo, useState } from "react";
import { api } from "../api";
import AudioPlayer from "./AudioPlayer";
import { useToast } from "../useToast";
import type { Question, Test } from "../types";

interface Props {
  test: Test;
  onCancel: () => void;
  onSubmitted: (graded: Test) => void;
}

function isMultipleChoice(q: Question): boolean {
  return q.options !== null && q.options.length > 0;
}

function isListening(q: Question): boolean {
  return q.question_type.startsWith("listening_");
}

export default function TakeTest({ test, onCancel, onSubmitted }: Props) {
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

  const question = test.questions[idx];
  const total = test.questions.length;
  const progressPct = useMemo(
    () => Math.round(((idx + 1) / total) * 100),
    [idx, total],
  );
  const answer = answers[question.id] ?? "";

  function setAnswer(value: string) {
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
  }

  function next() {
    if (idx < total - 1) setIdx(idx + 1);
  }
  function prev() {
    if (idx > 0) setIdx(idx - 1);
  }

  async function submit() {
    setSubmitting(true);
    setError(null);
    try {
      const graded = await api.submitTest(
        test.id,
        test.questions.map((q) => ({
          question_id: q.id,
          answer: answers[q.id] ?? "",
        })),
      );
      onSubmitted(graded);
    } catch (e) {
      const msg = (e as Error).message;
      setError(msg);
      showToast({
        kind: "error",
        title: "Could not submit test",
        message: msg,
      });
    } finally {
      setSubmitting(false);
    }
  }

  const answeredCount = test.questions.filter((q) =>
    (answers[q.id] ?? "").trim().length > 0,
  ).length;

  return (
    <div className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            Question {idx + 1} of {total}
          </span>
          <span>
            {answeredCount}/{total} answered
          </span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full bg-indigo-500 transition-all"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div>
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {questionTypeLabel(question.question_type)}
        </div>
        <h2 className="mt-1 text-xl font-semibold text-slate-900">
          {question.prompt}
        </h2>
      </div>

      {isListening(question) && question.audio_text && (
        <AudioPlayer text={question.audio_text} />
      )}

      {isMultipleChoice(question) ? (
        <MultipleChoice
          options={question.options ?? []}
          value={answer}
          onChange={setAnswer}
        />
      ) : (
        <FreeText
          value={answer}
          onChange={setAnswer}
          placeholder={freeTextPlaceholder(question)}
        />
      )}

      <Dots
        questions={test.questions}
        answers={answers}
        currentIdx={idx}
        onJump={setIdx}
      />

      {error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
          {error}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:border-slate-300"
        >
          Cancel
        </button>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={prev}
            disabled={idx === 0}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          {idx < total - 1 ? (
            <button
              type="button"
              onClick={next}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={submit}
              disabled={submitting}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Grading…" : "Submit test"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function questionTypeLabel(t: Question["question_type"]): string {
  switch (t) {
    case "kr_to_en_multiple_choice":
      return "Korean → English · multiple choice";
    case "en_to_kr_multiple_choice":
      return "English → Korean · multiple choice";
    case "kr_to_en_free_text":
      return "Korean → English · type the answer";
    case "en_to_kr_free_text":
      return "English → Korean · type the answer";
    case "listening_multiple_choice":
      return "Listening · multiple choice";
    case "listening_free_text":
      return "Listening · type the answer";
  }
}

function freeTextPlaceholder(q: Question): string {
  if (q.question_type === "en_to_kr_free_text") return "Hangul or romanization";
  return "Type your answer";
}

function MultipleChoice({
  options,
  value,
  onChange,
}: {
  options: string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="grid gap-2">
      {options.map((opt) => {
        const selected = value === opt;
        return (
          <button
            type="button"
            key={opt}
            onClick={() => onChange(opt)}
            className={
              "rounded-lg border px-4 py-3 text-left text-sm transition " +
              (selected
                ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200"
                : "border-slate-200 bg-white hover:border-slate-300")
            }
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

function FreeText({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      autoFocus
      className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-200"
    />
  );
}

function Dots({
  questions,
  answers,
  currentIdx,
  onJump,
}: {
  questions: Question[];
  answers: Record<number, string>;
  currentIdx: number;
  onJump: (idx: number) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {questions.map((q, i) => {
        const answered = (answers[q.id] ?? "").trim().length > 0;
        const current = i === currentIdx;
        return (
          <button
            key={q.id}
            type="button"
            aria-label={`Jump to question ${i + 1}`}
            onClick={() => onJump(i)}
            className={
              "h-6 w-6 rounded-full text-[10px] font-semibold transition " +
              (current
                ? "bg-indigo-600 text-white ring-2 ring-indigo-300"
                : answered
                  ? "bg-indigo-100 text-indigo-700 hover:bg-indigo-200"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200")
            }
          >
            {i + 1}
          </button>
        );
      })}
    </div>
  );
}

