import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useToast } from "../useToast";

interface Props {
  /** Korean text to synthesize. */
  text: string;
  /** Small UI mode renders a compact inline button (used in history rows). */
  variant?: "card" | "inline";
}

/**
 * Fetches TTS audio from the backend proxy via fetch() so we can inspect
 * the HTTP status. On failure we surface a toast and keep the rest of the
 * app usable (permissive degradation).
 */
export default function AudioPlayer({ text, variant = "card" }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const { showToast } = useToast();

  useEffect(() => {
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [blobUrl]);

  useEffect(() => {
    setBlobUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
  }, [text]);

  async function ensureAudio(): Promise<string | null> {
    if (blobUrl) return blobUrl;
    setLoading(true);
    try {
      const res = await fetch(api.ttsUrl(text));
      if (!res.ok) {
        let detail = `${res.status} ${res.statusText}`;
        try {
          const body = await res.json();
          if (body?.detail) detail = body.detail;
        } catch {
          /* ignore */
        }
        if (res.status === 503) {
          showToast({
            kind: "warning",
            title: "OpenAI API key not configured",
            message:
              "Audio is disabled. Set OPENAI_API_KEY in backend/.env and restart the backend to enable listening mode.",
          });
        } else {
          showToast({
            kind: "error",
            title: "OpenAI TTS failed",
            message: `${detail}. Your key may be invalid or rate-limited. The rest of the test still works.`,
          });
        }
        return null;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setBlobUrl(url);
      return url;
    } catch (e) {
      showToast({
        kind: "error",
        title: "Could not reach the audio service",
        message: (e as Error).message,
      });
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function play() {
    const url = await ensureAudio();
    const el = audioRef.current;
    if (!url || !el) return;
    try {
      if (el.src !== url) el.src = url;
      el.currentTime = 0;
      await el.play();
    } catch (e) {
      showToast({
        kind: "error",
        title: "Playback failed",
        message: (e as Error).message || "Could not play audio.",
      });
    }
  }

  if (variant === "inline") {
    return (
      <>
        <button
          type="button"
          onClick={play}
          disabled={loading}
          className="rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Loading…" : playing ? "▶ Playing" : "▶ Play"}
        </button>
        <audio
          ref={audioRef}
          preload="none"
          onPlay={() => setPlaying(true)}
          onEnded={() => setPlaying(false)}
          onPause={() => setPlaying(false)}
        />
      </>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <button
        type="button"
        onClick={play}
        disabled={loading}
        className="flex items-center gap-2 rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Loading…" : playing ? "▶ Playing…" : "▶ Play audio"}
      </button>
      <audio
        ref={audioRef}
        preload="none"
        onPlay={() => setPlaying(true)}
        onEnded={() => setPlaying(false)}
        onPause={() => setPlaying(false)}
      />
      <p className="mt-2 text-xs text-slate-500">
        Press play as many times as you need. The Korean spelling is hidden
        until you submit.
      </p>
    </div>
  );
}
