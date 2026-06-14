"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function IntakePage() {
  const t = useTranslations("intake");
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    native_language: "es",
    years_in_us: "",
    prior_english_study: "no",
    highest_education: "",
    primary_goal: "",
    age_band: "adult",
    language_preference: "bilingual",
  });
  const [error, setError] = useState("");

  const update = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        years_in_us: parseInt(form.years_in_us, 10),
      };
      const data = await api("/onboarding/intake", { method: "POST", body: JSON.stringify(payload) });
      localStorage.setItem("token", data.access_token);
      router.push("/onboarding/consent");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-6">{t("title")}</h1>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <input required placeholder="Email" value={form.email} onChange={(e) => update("email", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required placeholder={t("nativeLanguage")} value={form.native_language} onChange={(e) => update("native_language", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required type="number" placeholder={t("yearsInUS")} value={form.years_in_us} onChange={(e) => update("years_in_us", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required placeholder={t("priorStudy")} value={form.prior_english_study} onChange={(e) => update("prior_english_study", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required placeholder={t("education")} value={form.highest_education} onChange={(e) => update("highest_education", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required placeholder={t("goal")} value={form.primary_goal} onChange={(e) => update("primary_goal", e.target.value)} className="rounded-lg border px-4 py-3" />
          <input required placeholder={t("ageBand")} value={form.age_band} onChange={(e) => update("age_band", e.target.value)} className="rounded-lg border px-4 py-3" />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" className="rounded-lg bg-brand-600 px-4 py-3 text-white font-medium hover:bg-brand-700">
            {t("continue")}
          </button>
        </form>
      </div>
    </main>
  );
}
