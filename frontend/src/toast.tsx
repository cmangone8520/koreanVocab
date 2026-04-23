import {
  useCallback,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { ToastContext, type ToastContextValue, type Toast } from "./toastContext";

/**
 * Lightweight in-app toast system. Used for permissive failures (e.g. a
 * missing / invalid OpenAI API key) so the app keeps working while still
 * surfacing the error to the user.
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback<ToastContextValue["showToast"]>(
    ({ kind, title, message, durationMs }) => {
      const id = nextId.current++;
      const duration = durationMs ?? (kind === "error" ? 6000 : 4000);
      setToasts((prev) => [...prev, { id, kind, title, message, durationMs: duration }]);
      if (duration > 0) {
        window.setTimeout(() => dismiss(id), duration);
      }
    },
    [dismiss],
  );

  const value = useMemo(() => ({ showToast, dismiss }), [showToast, dismiss]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        aria-live="polite"
        className="pointer-events-none fixed inset-x-0 top-4 z-50 flex flex-col items-center gap-2 px-4"
      >
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const palette = {
    info: "border-sky-200 bg-sky-50 text-sky-900",
    success: "border-emerald-200 bg-emerald-50 text-emerald-900",
    warning: "border-amber-200 bg-amber-50 text-amber-900",
    error: "border-rose-200 bg-rose-50 text-rose-900",
  }[toast.kind];

  return (
    <div
      role="status"
      className={
        "pointer-events-auto w-full max-w-md rounded-lg border px-4 py-3 shadow-md " +
        palette
      }
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">{toast.title}</div>
          {toast.message && (
            <div className="mt-1 text-xs leading-relaxed opacity-90">
              {toast.message}
            </div>
          )}
        </div>
        <button
          onClick={onDismiss}
          aria-label="Dismiss notification"
          className="text-xs font-medium opacity-60 hover:opacity-100"
        >
          ✕
        </button>
      </div>
    </div>
  );
}


