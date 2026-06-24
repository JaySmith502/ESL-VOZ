"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";

type Cell = {
  mode: string;
  cefr_band: string;
  domain: string;
  mastery_score: number;
  confidence: number;
};

type Intervention = {
  id: string;
  rationale: string;
  created_at: string;
};

const MODES = ["Listening", "Speaking", "Reading", "Writing"];
const BANDS = ["A1.1", "A1.2", "A2.1", "A2.2"];

function cellColor(score: number): string {
  if (score >= 0.85) return "bg-green-500";
  if (score >= 0.5) return "bg-yellow-400";
  if (score > 0) return "bg-orange-300";
  return "bg-gray-100";
}

export default function StudentPage() {
  const { student_id } = useParams();
  const [student, setStudent] = useState<any>(null);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [note, setNote] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const loadInterventions = () =>
    api(`/instructor/students/${student_id}/interventions`).then(setInterventions);

  useEffect(() => {
    api(`/instructor/students/${student_id}`)
      .then(setStudent)
      .catch((err) => setError(err.message));
    loadInterventions().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [student_id]);

  const getCell = (mode: string, band: string) =>
    student?.cells.find((c: Cell) => c.mode === mode && c.cefr_band === band);

  const recordIntervention = async () => {
    if (!note.trim()) return;
    await api("/instructor/intervention", {
      method: "POST",
      body: JSON.stringify({ student_id, note }),
    });
    setNote("");
    setSaved(true);
    await loadInterventions();
    // Auto-clear the confirmation so the panel doesn't feel sticky on the
    // instructor's next visit to the same page.
    setTimeout(() => setSaved(false), 3000);
  };

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center p-6">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-3xl">
        <div className="flex items-start justify-between mb-1 print:block">
          <h1 className="text-2xl font-bold">{student?.email}</h1>
          {/* Browser-native print → PDF. No new dep. The action panel hides
              via @media print so the report stays clean. */}
          <button
            onClick={() => window.print()}
            className="rounded-lg border px-3 py-1 text-sm hover:bg-gray-50 print:hidden"
          >
            Print / PDF
          </button>
        </div>
        <p className="text-gray-600 mb-6">
          Level: {student?.cefr_band} · L1: {student?.l1}
        </p>

        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Mastery Matrix</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left p-2">Mode</th>
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

        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-2">Recent Recommendations</h2>
          {student?.recent_recommendations?.length ? (
            <ul className="text-sm space-y-2">
              {student.recent_recommendations.map((r: any, i: number) => (
                <li key={i} className="border-b pb-2 last:border-0">
                  <span className="font-medium">{r.lesson_id}</span>
                  <span className="text-gray-500 ml-2">bucket {r.bucket}</span>
                  <p className="text-gray-600">{r.rationale}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No activity yet.</p>
          )}
        </div>

        {/* Audit table — roadmap §M1 Flag/Note "audit table" requirement. */}
        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-2">Intervention History</h2>
          {interventions.length === 0 ? (
            <p className="text-sm text-gray-500">No interventions recorded yet.</p>
          ) : (
            <ul className="text-sm space-y-2">
              {interventions.map((it) => (
                <li key={it.id} className="border-b pb-2 last:border-0">
                  <p className="text-gray-600 whitespace-pre-wrap">{it.rationale}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(it.created_at).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow p-6 print:hidden">
          <h2 className="text-lg font-semibold mb-2">Intervention</h2>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 mb-3"
            rows={3}
            placeholder="Add a note for this student..."
          />
          <div className="flex items-center gap-3">
            <button
              onClick={recordIntervention}
              disabled={!note.trim()}
              className="rounded-lg bg-red-600 px-6 py-3 text-white font-medium hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Flag for Review
            </button>
            {saved && (
              <p className="text-green-600 text-sm" role="status">
                Recorded.
              </p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
