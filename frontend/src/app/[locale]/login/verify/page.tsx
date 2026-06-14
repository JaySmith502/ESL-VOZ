"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useRouter } from "@/i18n/routing";
import { api } from "@/lib/api";

export default function VerifyPage() {
  const t = useTranslations("verify");
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api("/auth/magic-link/verify", { method: "POST", body: JSON.stringify({ token }) })
      .then((data) => {
        localStorage.setItem("token", data.access_token);
        router.push("/onboarding/intake");
      })
      .catch((err) => setError(err.message));
  }, [token, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="text-center">
        <p className="text-lg">{error || t("verifying")}</p>
        {error && <p className="text-red-600 mt-2">{t("error")}</p>}
      </div>
    </main>
  );
}
