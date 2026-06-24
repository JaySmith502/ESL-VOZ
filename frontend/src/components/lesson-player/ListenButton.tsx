"use client";

import { useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Plays TTS audio for `text` via POST /tutor/tts.
 *
 * Degrades silently when the backend returns 503 (no OpenAI key): the button
 * just disables itself for the rest of the session — the lesson text is on
 * screen anyway, so the learner isn't blocked.
 */
export function ListenButton({ text }: { text: string }) {
  const [loading, setLoading] = useState(false);
  const [disabled, setDisabled] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const play = async () => {
    if (loading || disabled) return;
    setLoading(true);
    try {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : "";
      const res = await fetch(`${API_BASE}/tutor/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ text }),
      });
      if (res.status === 503) {
        // Backend has no TTS key wired — hide the button for the rest of the
        // session rather than nagging the learner with a popup.
        setDisabled(true);
        return;
      }
      if (!res.ok) throw new Error(`TTS ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      // Reuse one Audio element so rapid clicks don't pile up.
      if (!audioRef.current) audioRef.current = new Audio();
      audioRef.current.src = url;
      // ponytail: leaks the prior blob URL on replay; revoke if memory matters.
      await audioRef.current.play();
    } catch {
      // One-off failures shouldn't break the lesson; silent retry on next click.
    } finally {
      setLoading(false);
    }
  };

  if (disabled) return null;

  return (
    <button
      type="button"
      onClick={play}
      disabled={loading}
      aria-label="Listen"
      className="rounded-full w-9 h-9 inline-flex items-center justify-center bg-gray-100 hover:bg-gray-200 text-gray-700 mr-2 align-middle"
    >
      {loading ? "…" : "🔊"}
    </button>
  );
}
