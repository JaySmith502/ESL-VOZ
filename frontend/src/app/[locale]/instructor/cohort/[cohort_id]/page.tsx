"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

type Student = {
  id: string;
  email: string;
  cefr_band: string;
  language_preference: string;
  avg_mastery: number;
  last_active: string | null;
};

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
              {cohort?.students.map((s) => (
                <tr
                  key={s.id}
                  className="border-t hover:bg-gray-50 cursor-pointer"
                  onClick={() => router.push(`/instructor/student/${s.id}`)}
                >
                  <td className="p-4">{s.email}</td>
                  <td className="p-4">{s.cefr_band}</td>
                  <td className="p-4">{Math.round(s.avg_mastery * 100)}%</td>
                  <td className="p-4">
                    {s.last_active ? new Date(s.last_active).toLocaleDateString() : "Never"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
