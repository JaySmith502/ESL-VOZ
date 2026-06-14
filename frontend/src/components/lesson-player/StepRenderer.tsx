"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { VoiceRecorder } from "./VoiceRecorder";

function normalize(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function scoreProduction(target: string, variants: string[] = [], answer: string): number {
  const normalizedAnswer = normalize(answer);
  const acceptable = [target, ...variants].map(normalize);
  if (acceptable.some((v) => v === normalizedAnswer)) return 1.0;
  // Partial credit for overlapping words
  const targetWords = normalize(target).split(" ");
  const answerWords = normalizedAnswer.split(" ");
  const overlap = targetWords.filter((w) => answerWords.includes(w)).length;
  return Math.min(1.0, overlap / Math.max(1, targetWords.length));
}

export function StepRenderer({
  step,
  onComplete,
}: {
  step: any;
  onComplete: (score: number) => void;
}) {
  const t = useTranslations("lesson");
  const config = step.config || {};

  switch (step.step_type) {
    case "intro":
      return (
        <div>
          <p className="text-lg mb-2">{step.prompt?.en}</p>
          <p className="text-gray-600 mb-6 italic">{step.prompt?.es}</p>
          <button
            onClick={() => onComplete(1.0)}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("continue")}
          </button>
        </div>
      );

    case "vocab_intro":
      return (
        <div>
          <p className="text-lg mb-2">{step.prompt?.en}</p>
          <p className="text-gray-600 mb-6 italic">{step.prompt?.es}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {config.words?.map((word: any, i: number) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3">
                <p className="font-medium">{word.en}</p>
                <p className="text-gray-500 text-sm">{word.es}</p>
              </div>
            ))}
          </div>
          <button
            onClick={() => onComplete(1.0)}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("continue")}
          </button>
        </div>
      );

    case "vocab_drill":
      return <VocabDrill items={config.items} onComplete={onComplete} t={t} />;

    case "production_speaking":
      return (
        <ProductionSpeaking
          target={config.target}
          acceptableVariants={config.acceptable_variants || []}
          onComplete={onComplete}
          t={t}
        />
      );

    case "reflection":
      return (
        <div>
          <p className="text-lg mb-2">{step.prompt?.en}</p>
          <p className="text-gray-600 mb-6 italic">{step.prompt?.es}</p>
          <button
            onClick={() => onComplete(1.0)}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("continue")}
          </button>
        </div>
      );

    default:
      return (
        <div>
          <p className="text-lg mb-2">{step.prompt?.en}</p>
          <p className="text-gray-600 mb-6 italic">{step.prompt?.es}</p>
          <button
            onClick={() => onComplete(1.0)}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("continue")}
          </button>
        </div>
      );
  }
}

function VocabDrill({
  items,
  onComplete,
  t,
}: {
  items: { prompt: string; answer: string }[];
  onComplete: (score: number) => void;
  t: any;
}) {
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState<boolean[]>([]);

  const item = items[index];

  const check = () => {
    const correct = normalize(answer) === normalize(item.answer);
    const nextResults = [...results, correct];
    if (index + 1 < items.length) {
      setResults(nextResults);
      setIndex(index + 1);
      setAnswer("");
    } else {
      const score = nextResults.filter(Boolean).length / nextResults.length;
      onComplete(score);
    }
  };

  return (
    <div>
      <p className="text-lg mb-4">
        {t("whatIsInSpanish") || "What is in Spanish?"}: <span className="font-bold">{item.prompt}</span>
      </p>
      <input
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && check()}
        className="w-full rounded-lg border px-4 py-2 mb-4"
        placeholder={t("typeAnswer")}
      />
      <button
        onClick={check}
        className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
      >
        {t("continue")}
      </button>
      <p className="mt-2 text-sm text-gray-500">
        {index + 1} / {items.length}
      </p>
    </div>
  );
}

function ProductionSpeaking({
  target,
  acceptableVariants,
  onComplete,
  t,
}: {
  target: string;
  acceptableVariants: string[];
  onComplete: (score: number) => void;
  t: any;
}) {
  const [answer, setAnswer] = useState("");
  const [checked, setChecked] = useState(false);
  const score = checked ? scoreProduction(target, acceptableVariants, answer) : 0;

  return (
    <div>
      <p className="text-lg mb-2">{t("sayThis") || "Say or type this in English"}:</p>
      <p className="bg-gray-100 p-3 rounded-lg mb-4 font-medium">{target}</p>
      <input
        value={answer}
        onChange={(e) => {
          setAnswer(e.target.value);
          setChecked(false);
        }}
        className="w-full rounded-lg border px-4 py-2 mb-4"
        placeholder={t("typeAnswer")}
      />
      <VoiceRecorder
        target={target}
        acceptableVariants={acceptableVariants}
        onResult={(score, transcript) => {
          setAnswer(transcript);
          setChecked(true);
        }}
      />
      {!checked ? (
        <button
          onClick={() => setChecked(true)}
          className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
        >
          {t("check") || "Check"}
        </button>
      ) : (
        <div>
          <p className={`mb-4 font-medium ${score >= 0.8 ? "text-green-600" : "text-amber-600"}`}>
            {score >= 0.8 ? t("correct") : t("tryAgain")}
          </p>
          {score < 0.8 && (
            <button
              onClick={() => {
                setAnswer("");
                setChecked(false);
              }}
              className="rounded-lg border px-6 py-3 font-medium mr-3 hover:bg-gray-50"
            >
              {t("tryAgain")}
            </button>
          )}
          <button
            onClick={() => onComplete(score)}
            className="rounded-lg bg-brand-600 px-6 py-3 text-white font-medium hover:bg-brand-700"
          >
            {t("continue")}
          </button>
        </div>
      )}
    </div>
  );
}
