"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type PlacementItem = {
  id: string;
  mode: string;
  band: string;
  prompt_en: string;
  prompt_es: string;
  options?: string[];
  example?: string;
};

export default function PlacementPage() {
  const t = useTranslations("placement");
  const router = useRouter();
  const [items, setItems] = useState<PlacementItem[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/onboarding/placement-items")
      .then((data) => setItems(data.items))
      .catch((err) => setError(err.message));
  }, []);

  const setAnswer = (id: string, value: string) =>
    setAnswers((a) => ({ ...a, [id]: value }));

  const idk = (id: string) => setAnswer(id, "__idk__");

  const submit = async () => {
    const data = await api("/onboarding/placement", {
      method: "POST",
      body: JSON.stringify({ answers }),
    });
    setResult(data);
    setSubmitted(true);
  };

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-6">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  if (submitted) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4">{t("completeTitle")}</h2>
          <p className="mb-2">{t("overallBand")}: {result?.overall_band}</p>
          <p className="mb-6 text-sm text-gray-600">
            {t("estimatedBands")}: {JSON.stringify(result?.estimated_bands)}
          </p>
          <button
            onClick={() => router.push("/learn")}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("goToLearn")}
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-2">{t("title")}</h1>
        <p className="text-gray-600 mb-6">{t("instructions")}</p>
        <div className="flex flex-col gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className={`border rounded-xl p-4 ${answers[item.id] === "__idk__" ? "bg-gray-50" : ""}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-semibold text-brand-700">
                  {item.mode} · {item.band}
                </span>
              </div>
              <p className="text-gray-900">{item.prompt_en}</p>
              <p className="text-gray-500 text-sm italic">{item.prompt_es}</p>
              {item.example && (
                <p className="text-gray-400 text-sm mt-1">
                  {t("example")}: {item.example}
                </p>
              )}
              {item.options ? (
                <div className="flex flex-wrap gap-3 mt-3">
                  {item.options.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => setAnswer(item.id, opt)}
                      className={`px-4 py-2 rounded-lg border ${answers[item.id] === opt ? "bg-brand-100 border-brand-600" : ""}`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              ) : (
                <input
                  value={answers[item.id] === "__idk__" ? "" : answers[item.id] || ""}
                  onChange={(e) => setAnswer(item.id, e.target.value)}
                  className="mt-3 w-full rounded-lg border px-4 py-2"
                  placeholder={t("typeAnswer")}
                />
              )}
              <button
                onClick={() => idk(item.id)}
                className="mt-3 text-sm text-gray-500 underline hover:text-brand-600"
              >
                {t("idk")}
              </button>
            </div>
          ))}
        </div>
        <button
          onClick={submit}
          className="mt-8 w-full rounded-lg bg-brand-600 px-4 py-3 text-white font-medium hover:bg-brand-700"
        >
          {t("submit")}
        </button>
      </div>
    </main>
  );
}
