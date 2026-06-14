"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { api } from "@/lib/api";

type MasteryCell = {
  mode: string;
  cefr_band: string;
  domain: string;
  mastery_score: number;
  confidence: number;
};

type Profile = {
  profile_id: string;
  cefr_band: string;
  language_preference: string;
  l1: string;
  mastery_cells: MasteryCell[];
};

const MODES = ["Listening", "Speaking", "Reading", "Writing"];
const BANDS = ["A1.1", "A1.2", "A2.1", "A2.2"];

function cellColor(score: number): string {
  if (score >= 0.85) return "bg-green-500";
  if (score >= 0.5) return "bg-yellow-400";
  if (score > 0) return "bg-orange-300";
  return "bg-gray-100";
}

export default function LearnPage() {
  const t = useTranslations("learn");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [rec, setRec] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api("/auth/me/profile"), api("/engine/next-activity")])
      .then(([profileData, recData]) => {
        setProfile(profileData);
        setRec(recData);
      })
      .catch((err) => setError(err.message));
  }, []);

  const getCell = (mode: string, band: string) =>
    profile?.mastery_cells.find((c) => c.mode === mode && c.cefr_band === band);

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-6">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-3xl">
        <h1 className="text-2xl font-bold mb-2 text-center">{t("title")}</h1>
        <p className="text-center text-gray-600 mb-6">
          {t("currentLevel")}: {profile?.cefr_band || "..."}
        </p>

        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{t("masteryMatrix")}</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left p-2">{t("mode")}</th>
                  {BANDS.map((band) => (
                    <th key={band} className="text-center p-2">
                      {band}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MODES.map((mode) => (
                  <tr key={mode}>
                    <td className="p-2 font-medium">{mode}</td>
                    {BANDS.map((band) => {
                      const cell = getCell(mode, band);
                      return (
                        <td key={band} className="p-2">
                          <div
                            className={`h-8 rounded ${cellColor(cell?.mastery_score || 0)} flex items-center justify-center text-xs`}
                            title={cell ? `${Math.round(cell.mastery_score * 100)}%` : ""}
                          >
                            {cell ? `${Math.round(cell.mastery_score * 100)}` : ""}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow p-6 text-center">
          <h2 className="text-lg font-semibold mb-2">{t("recommended")}</h2>
          {rec?.activity?.lesson_id ? (
            <>
              <p className="text-xl font-medium mb-1">{rec.activity.title_en}</p>
              <p className="text-gray-600 mb-2">{rec.activity.title_es}</p>
              <p className="text-sm text-gray-500 mb-4">
                {t("why")}: {rec.rationale}
              </p>
              <Link
                href={`/learn/lesson/${rec.activity.lesson_id}`}
                className="inline-block rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
              >
                {t("start")}
              </Link>
            </>
          ) : (
            <p>{t("noActivity")}</p>
          )}
        </div>
      </div>
    </main>
  );
}
