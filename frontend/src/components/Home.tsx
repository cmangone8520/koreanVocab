import { useEffect, useState } from "react";
import { api } from "../api";
import type { LevelSummary, Test, TestSummary } from "../types";

interface Props {
  levels: LevelSummary[];
  openaiConfigured: boolean;
  onStart: () => void;
  onOpen: (test: Test) => void;
  refreshKey: number;
}

export default function Home({
  levels,
  openaiConfigured,
  onStart,
  onOpen,
  refreshKey,
}: Props) {
  const [history, setHistory] = useState<TestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const h = await api.listTests();
        if (!cancelled) setHistory(h);
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  async function handleDelete(id: number) {
    try {
      await api.deleteTest(id);
      setHistory((prev) => prev.filter((t) => t.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function handleOpen(id: number) {
    try {
      const t = await api.getTest(id);
      onOpen(t);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Start practicing</h2>
        <p className="mt-1 text-sm text-slate-600">
          Pick an experience level and question mix, and we&rsquo;ll generate
          a fresh test for you.
        </p>
        <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs text-slate-600">
          {levels.map((l) => (
            <div
              key={l.level}
              className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
            >
              <div className="text-sm font-medium capitalize text-slate-800">
                {l.level}
              </div>
              <div>{l.word_count} words</div>
            </div>
          ))}
        </div>
        <button
          onClick={onStart}
          className="mt-5 w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Start a new test
        </button>
        {!openaiConfigured && (
          <p className="mt-2 text-center text-xs text-slate-500">
            Listening mode is disabled until you configure OPENAI_API_KEY.
          </p>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">History</h2>
          {loading && <span className="text-xs text-slate-500">Loading…</span>}
        </div>
        {error && (
          <div className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
            {error}
          </div>
        )}
        {!loading && history.length === 0 && !error && (
          <p className="mt-3 text-sm text-slate-500">
            No tests yet — take your first one above.
          </p>
        )}
        {history.length > 0 && (
          <ul className="mt-3 divide-y divide-slate-100">
            {history.map((t) => {
              const completed = t.completed_at !== null;
              const pct =
                completed && t.score !== null && t.total
                  ? Math.round((t.score / t.total) * 100)
                  : null;
              return (
                <li
                  key={t.id}
                  className="flex items-center justify-between gap-3 py-3"
                >
                  <button
                    className="flex-1 text-left"
                    onClick={() => handleOpen(t.id)}
                  >
                    <div className="text-sm font-medium text-slate-800">
                      <span className="capitalize">{t.level}</span>{" "}
                      <span className="text-slate-400">·</span>{" "}
                      <span className="capitalize">{t.mode}</span>{" "}
                      <span className="text-slate-400">·</span>{" "}
                      {t.num_questions} questions
                    </div>
                    <div className="mt-0.5 text-xs text-slate-500">
                      {new Date(t.created_at + "Z").toLocaleString()} —{" "}
                      {completed
                        ? `${t.score}/${t.total} (${pct}%)`
                        : "in progress"}
                    </div>
                  </button>
                  <button
                    onClick={() => handleDelete(t.id)}
                    className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-500 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
                    aria-label={`Delete test ${t.id}`}
                  >
                    Delete
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
