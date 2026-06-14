"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function ConsentPage() {
  const t = useTranslations("consent");
  const router = useRouter();
  const [platformTerms, setPlatformTerms] = useState(false);
  const [voiceAudio, setVoiceAudio] = useState(false);
  const [anonymizedSharing, setAnonymizedSharing] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/onboarding/consent", {
        method: "POST",
        body: JSON.stringify({ platform_terms: platformTerms, voice_audio: voiceAudio, anonymized_sharing: anonymizedSharing }),
      });
      router.push("/onboarding/placement");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-6">{t("title")}</h1>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <label className="flex items-center gap-3">
            <input type="checkbox" required checked={platformTerms} onChange={(e) => setPlatformTerms(e.target.checked)} />
            <span>{t("platformTerms")}</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={voiceAudio} onChange={(e) => setVoiceAudio(e.target.checked)} />
            <span>{t("voiceAudio")}</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={anonymizedSharing} onChange={(e) => setAnonymizedSharing(e.target.checked)} />
            <span>{t("anonymizedSharing")}</span>
          </label>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" className="rounded-lg bg-brand-600 px-4 py-3 text-white font-medium hover:bg-brand-700">
            {t("submit")}
          </button>
        </form>
      </div>
    </main>
  );
}
