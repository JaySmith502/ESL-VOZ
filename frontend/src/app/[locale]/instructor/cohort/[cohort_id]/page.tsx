"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useRouter } from "@/i18n/routing";
import { api } from "@/lib/api";

type Student = {
  id: string;
  email: string;
  cefr_band: string;
  language_preference: string;
  avg_mastery: number;
  last_active: string | null;
};

// Same thresholds across the dashboard so the "Needs attention" panel and the
// row highlight in the full table agree.
const STALE_DAYS = 7;
const LOW_MASTERY = 0.4;

function needsAttention(s: Student): { reason: string } | null {
  if (s.avg_mastery < LOW_MASTERY) return { reason: `Avg mastery ${Math.round(s.avg_mastery * 100)}%` };
  if (!s.last_active) return { reason: "Never started" };
  const daysSince =
    (Date.now() - new Date(s.last_active).getTime()) / (1000 * 60 * 60 * 24);
  if (daysSince > STALE_DAYS) return { reason: `Inactive ${Math.round(daysSince)}d` };
  return null;
}

export default function CohortPage() {
  const { cohort_id } = useParams();
  const router = useRouter();
  const [cohort, setCohort] = useState<{ name: string; students: Student[] } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/instructor/cohorts/${cohort_id}`)
      .then(setCohort)
      .catch((err) => setError(err.message));
  }, [cohort_id]);

  const flagged = useMemo(
    () =>
      (cohort?.students || [])
        .map((s) => ({ s, flag: needsAttention(s) }))
        .filter((row) => row.flag),
    [cohort],
  );

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center p-6">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-4xl">
        <h1 className="text-2xl font-bold mb-2">{cohort?.name}</h1>
        <p className="text-gray-600 mb-6">{cohort?.students.length} students</p>

        {/* Needs attention — the first lens an instructor wants on each visit.
            Hidden when nobody qualifies so the page stays calm. */}
        {flagged.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 mb-6">
            <h2 className="text-lg font-semibold mb-3 text-amber-900">
              Needs attention ({flagged.length})
            </h2>
            <ul className="text-sm space-y-2">
              {flagged.map(({ s, flag }) => (
                <li key={s.id} className="flex items-center justify-between">
                  <button
                    onClick={() => router.push(`/instructor/student/${s.id}`)}
                    className="text-left hover:underline"
                  >
                    {s.email}
                  </button>
                  <span className="text-amber-800 text-xs">{flag!.reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-4">Email</th>
                <th className="p-4">Level</th>
                <th className="p-4">Avg Mastery</th>
                <th className="p-4">Last Active</th>
              </tr>
            </thead>
            <tbody>
              {cohort?.students.map((s) => {
                const flag = needsAttention(s);
                return (
                  <tr
                    key={s.id}
                    className={`border-t hover:bg-gray-50 cursor-pointer ${flag ? "bg-amber-50/40" : ""}`}
                    onClick={() => router.push(`/instructor/student/${s.id}`)}
                  >
                    <td className="p-4">{s.email}</td>
                    <td className="p-4">{s.cefr_band}</td>
                    <td className="p-4">{Math.round(s.avg_mastery * 100)}%</td>
                    <td className="p-4">
                      {s.last_active ? new Date(s.last_active).toLocaleDateString() : "Never"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
