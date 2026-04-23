import AudioPlayer from "./AudioPlayer";
import type { Question, Test } from "../types";

interface Props {
  test: Test;
  onHome: () => void;
  onAnother: () => void;
}

export default function Results({ test, onHome, onAnother }: Props) {
  const score = test.score ?? 0;
  const total = test.total ?? test.questions.length;
  const pct = total === 0 ? 0 : Math.round((score / total) * 100);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-end justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Results · <span className="capitalize">{test.level}</span>{" "}
              <span className="text-slate-400">·</span>{" "}
              <span className="capitalize">{test.mode}</span>
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              {score} correct out of {total}.
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-indigo-600">{pct}%</div>
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={onAnother}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            Take another
          </button>
          <button
            type="button"
            onClick={onHome}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-slate-300"
          >
            Back to home
          </button>
        </div>
      </section>

      <section className="space-y-3">
        {test.questions.map((q, i) => (
          <ResultRow key={q.id} question={q} index={i + 1} />
        ))}
      </section>
    </div>
  );
}

function ResultRow({ question, index }: { question: Question; index: number }) {
  const correct = question.is_correct === true;
  return (
    <div
      className={
        "rounded-xl border p-4 shadow-sm " +
        (correct
          ? "border-emerald-200 bg-emerald-50"
          : "border-rose-200 bg-rose-50")
      }
    >
      <div className="flex items-center justify-between text-xs font-medium uppercase tracking-wide text-slate-500">
        <span>
          #{index} · {questionTypeLabel(question.question_type)}
        </span>
        <span
          className={correct ? "text-emerald-700" : "text-rose-700"}
        >
          {correct ? "Correct" : "Incorrect"}
        </span>
      </div>
      <div className="mt-1 text-sm text-slate-800">{question.prompt}</div>

      {question.audio_text && (
        <div className="mt-2">
          <AudioPlayer text={question.audio_text} variant="inline" />
        </div>
      )}

      <div className="mt-3 grid gap-1 text-sm">
        <div>
          <span className="text-slate-500">Your answer: </span>
          <span
            className={
              correct
                ? "font-medium text-emerald-800"
                : "font-medium text-rose-800"
            }
          >
            {question.user_answer?.trim() ? question.user_answer : "(blank)"}
          </span>
        </div>
        {!correct && question.correct_answer && (
          <div>
            <span className="text-slate-500">Correct answer: </span>
            <span className="font-medium text-slate-900">
              {question.correct_answer}
            </span>
          </div>
        )}
        {question.audio_text && (
          <div className="text-xs text-slate-500">
            Korean spelling: <span className="font-medium">{question.audio_text}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function questionTypeLabel(t: Question["question_type"]): string {
  switch (t) {
    case "kr_to_en_multiple_choice":
      return "Korean → English (MC)";
    case "en_to_kr_multiple_choice":
      return "English → Korean (MC)";
    case "kr_to_en_free_text":
      return "Korean → English";
    case "en_to_kr_free_text":
      return "English → Korean";
    case "listening_multiple_choice":
      return "Listening (MC)";
    case "listening_free_text":
      return "Listening";
  }
}
