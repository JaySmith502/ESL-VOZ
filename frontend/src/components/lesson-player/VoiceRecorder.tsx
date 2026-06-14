"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";

export function VoiceRecorder({
  target,
  acceptableVariants,
  onResult,
}: {
  target: string;
  acceptableVariants: string[];
  onResult: (score: number, transcript: string) => void;
}) {
  const [recording, setRecording] = useState(false);
  const [feedback, setFeedback] = useState("");
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const media = new MediaRecorder(stream);
    mediaRef.current = media;
    chunksRef.current = [];
    media.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    media.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");
      formData.append("target", target);
      try {
        const data = await api("/tutor/subdialog/audio", {
          method: "POST",
          body: formData,
        });
        setFeedback(data.feedback_en);
        onResult(data.score, data.transcript);
      } catch (err: any) {
        setFeedback(err.message);
      }
    };
    media.start();
    setRecording(true);
  };

  const stop = () => {
    mediaRef.current?.stop();
    setRecording(false);
  };

  return (
    <div className="mt-4">
      <button
        onClick={recording ? stop : start}
        className={`rounded-full w-12 h-12 flex items-center justify-center text-white ${recording ? "bg-red-600" : "bg-brand-600"}`}
        type="button"
      >
        {recording ? "■" : "🎤"}
      </button>
      {feedback && <p className="mt-2 text-sm text-gray-700">{feedback}</p>}
    </div>
  );
}
