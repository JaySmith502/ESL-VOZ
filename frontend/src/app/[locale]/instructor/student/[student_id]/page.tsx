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
  const [note, setNote] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/instructor/students/${student_id}`)
      .then(setStudent)
      .catch((err) => setError(err.message));
  }, [student_id]);

  const getCell = (mode: string, band: string) =>
    student?.cells.find((c: Cell) => c.mode === mode && c.cefr_band === band);

  const recordIntervention = async () => {
    await api("/instructor/intervention", {
      method: "POST",
      body: JSON.stringify({ student_id, note }),
    });
    setNote("");
    alert("Intervention recorded");
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
        <h1 className="text-2xl font-bold mb-1">{student?.email}</h1>
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
          <ul className="text-sm space-y-2">
            {student?.recent_recommendations.map((r: any, i: number) => (
              <li key={i} className="border-b pb-2 last:border-0">
                <span className="font-medium">{r.lesson_id}</span>
                <span className="text-gray-500 ml-2">bucket {r.bucket}</span>
                <p className="text-gray-600">{r.rationale}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Intervention</h2>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 mb-3"
            rows={3}
            placeholder="Add a note for this student..."
          />
          <button
            onClick={recordIntervention}
            className="rounded-lg bg-red-600 px-6 py-3 text-white font-medium hover:bg-red-700"
          >
            Flag for Review
          </button>
        </div>
      </div>
    </main>
  );
}
