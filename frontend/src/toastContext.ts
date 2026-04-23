import { createContext } from "react";

export type ToastKind = "info" | "success" | "warning" | "error";

export interface Toast {
  id: number;
  kind: ToastKind;
  title: string;
  message?: string;
  durationMs: number;
}

export interface ToastContextValue {
  showToast: (t: Omit<Toast, "id" | "durationMs"> & { durationMs?: number }) => void;
  dismiss: (id: number) => void;
}

export const ToastContext = createContext<ToastContextValue | null>(null);
