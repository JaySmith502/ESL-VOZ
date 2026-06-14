"use client";

import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/routing";
import { api } from "@/lib/api";

type Cohort = {
  id: string;
  name: string;
  status: string;
  student_count: number;
};

export default function InstructorPage() {
  const router = useRouter();
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/instructor/cohorts")
      .then((data) => setCohorts(data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-4xl">
        <h1 className="text-2xl font-bold mb-6">Instructor Dashboard</h1>
        {error ? (
          <p className="text-red-600">{error}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cohorts.map((cohort) => (
              <button
                key={cohort.id}
                onClick={() => router.push(`/instructor/cohort/${cohort.id}`)}
                className="text-left bg-white rounded-2xl shadow p-6 hover:shadow-md transition"
              >
                <h2 className="text-xl font-semibold">{cohort.name}</h2>
                <p className="text-gray-600 mt-1">{cohort.student_count} students</p>
                <p className="text-sm text-gray-400 capitalize">{cohort.status}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
