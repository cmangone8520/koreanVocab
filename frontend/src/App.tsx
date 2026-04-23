import { useEffect, useState } from "react";
import { api } from "./api";
import Home from "./components/Home";
import TestSetup from "./components/TestSetup";
import TakeTest from "./components/TakeTest";
import Results from "./components/Results";
import { useToast } from "./useToast";
import type { Health, LevelSummary, Test } from "./types";

type View =
  | { kind: "home" }
  | { kind: "setup" }
  | { kind: "take"; test: Test }
  | { kind: "results"; test: Test };

export default function App() {
  const [view, setView] = useState<View>({ kind: "home" });
  const [health, setHealth] = useState<Health | null>(null);
  const [levels, setLevels] = useState<LevelSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [historyBump, setHistoryBump] = useState(0);
  const { showToast } = useToast();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [h, l] = await Promise.all([api.healthz(), api.listLevels()]);
        if (cancelled) return;
        setHealth(h);
        setLevels(l);
        if (!h.openai_configured) {
          showToast({
            kind: "warning",
            title: "OpenAI API key not configured",
            message:
              "Listening mode is disabled. Set OPENAI_API_KEY in backend/.env and restart the backend to enable audio.",
            durationMs: 8000,
          });
        }
      } catch (e) {
        if (!cancelled) {
          const msg = (e as Error).message;
          setError(msg);
          showToast({
            kind: "error",
            title: "Backend unreachable",
            message: msg,
          });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen w-full">
      <header className="mx-auto max-w-3xl px-6 pt-10 pb-4">
        <button
          onClick={() => setView({ kind: "home" })}
          className="text-left"
        >
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Korean Vocab
            <span className="ml-2 align-middle text-2xl">한국어</span>
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Practice written and listening translations.
          </p>
        </button>
        {health && !health.openai_configured && (
          <div className="mt-4 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
            OpenAI API key not configured &mdash; listening mode is disabled.
            Set <code className="font-mono">OPENAI_API_KEY</code> in{" "}
            <code className="font-mono">backend/.env</code> and restart the
            backend to enable audio.
          </div>
        )}
        {error && (
          <div className="mt-4 rounded-lg border border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-900">
            Failed to reach the backend: {error}. Is it running on
            <code className="font-mono"> http://localhost:8000</code>?
          </div>
        )}
      </header>

      <main className="mx-auto max-w-3xl px-6 pb-20">
        {view.kind === "home" && (
          <Home
            levels={levels}
            openaiConfigured={health?.openai_configured ?? false}
            onStart={() => setView({ kind: "setup" })}
            onOpen={(test) =>
              setView({
                kind: test.completed_at ? "results" : "take",
                test,
              })
            }
            refreshKey={historyBump}
          />
        )}
        {view.kind === "setup" && (
          <TestSetup
            levels={levels}
            openaiConfigured={health?.openai_configured ?? false}
            onCancel={() => setView({ kind: "home" })}
            onCreated={(t) => setView({ kind: "take", test: t })}
          />
        )}
        {view.kind === "take" && (
          <TakeTest
            test={view.test}
            onCancel={() => setView({ kind: "home" })}
            onSubmitted={(graded) => {
              setHistoryBump((n) => n + 1);
              setView({ kind: "results", test: graded });
            }}
          />
        )}
        {view.kind === "results" && (
          <Results
            test={view.test}
            onHome={() => {
              setHistoryBump((n) => n + 1);
              setView({ kind: "home" });
            }}
            onAnother={() => setView({ kind: "setup" })}
          />
        )}
      </main>
    </div>
  );
}
