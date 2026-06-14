"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";

export default function SplashPage() {
  const t = useTranslations("splash");
  const router = useRouter();

  const choose = (locale: string) => {
    router.push(`/${locale}/login`);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <h1 className="text-4xl font-bold text-brand-700 mb-2">{t("title")}</h1>
      <p className="text-lg text-gray-600 mb-10">{t("subtitle")}</p>
      <div className="flex flex-col gap-4 w-full max-w-xs">
        <button
          onClick={() => choose("es")}
          className="rounded-xl bg-brand-600 px-6 py-4 text-white text-lg font-medium hover:bg-brand-700 transition"
        >
          {t("spanish")}
        </button>
        <button
          onClick={() => choose("en")}
          className="rounded-xl bg-brand-600 px-6 py-4 text-white text-lg font-medium hover:bg-brand-700 transition"
        >
          {t("english")}
        </button>
        <button
          onClick={() => choose("es")}
          className="rounded-xl border-2 border-brand-600 px-6 py-4 text-brand-700 text-lg font-medium hover:bg-brand-50 transition"
        >
          {t("bilingual")}
        </button>
      </div>
    </main>
  );
}
