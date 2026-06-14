"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Link } from "@/i18n/routing";
import { api } from "@/lib/api";
import { StepRenderer } from "@/components/lesson-player/StepRenderer";

export default function LessonPage() {
  const { lesson_id } = useParams();
  const [lesson, setLesson] = useState<any>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    api(`/lessons/${lesson_id}`).then(setLesson);
  }, [lesson_id]);

  const submitStep = async (score: number) => {
    const step = lesson.steps[stepIndex];
    await api(`/lessons/${lesson_id}/attempt`, {
      method: "POST",
      body: JSON.stringify({
        step_id: step.step_id,
        score,
        response: {},
      }),
    });
    if (stepIndex + 1 < lesson.steps.length) {
      setStepIndex(stepIndex + 1);
    } else {
      setFinished(true);
    }
  };

  if (!lesson) return <main className="p-6">Loading...</main>;

  if (finished) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Lesson complete!</h2>
          <Link href="/learn" className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700 inline-block">
            Back to Learn
          </Link>
        </div>
      </main>
    );
  }

  const step = lesson.steps[stepIndex];

  return (
    <main className="flex min-h-screen flex-col items-center p-6">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-2">{lesson.title_en}</h1>
        <p className="text-gray-600 mb-6">{lesson.title_es}</p>
        <StepRenderer step={step} onComplete={submitStep} />
      </div>
    </main>
  );
}
