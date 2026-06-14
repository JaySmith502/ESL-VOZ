"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";

export default function LoginPage() {
  const t = useTranslations("login");
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/auth/magic-link", { method: "POST", body: JSON.stringify({ email }) });
      setSent(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow p-8">
        <h1 className="text-2xl font-bold mb-6 text-center">{t("title")}</h1>
        {sent ? (
          <p className="text-center text-green-700">{t("checkingEmail")}</p>
        ) : (
          <form onSubmit={submit} className="flex flex-col gap-4">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("emailPlaceholder")}
              className="rounded-lg border px-4 py-3"
            />
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button
              type="submit"
              className="rounded-lg bg-brand-600 px-4 py-3 text-white font-medium hover:bg-brand-700"
            >
              {t("sendLink")}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
