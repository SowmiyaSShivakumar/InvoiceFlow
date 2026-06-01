"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, requestJson, type LogoutRequest } from "../../lib/api";
import { clearAuthTokens, readRefreshToken } from "../../lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onLogout() {
    setLoading(true);
    setError(null);

    const refreshToken = readRefreshToken();
    if (!refreshToken) {
      clearAuthTokens();
      setLoading(false);
      router.push("/login");
      return;
    }

    const payload: LogoutRequest = { refresh_token: refreshToken };

    try {
      await requestJson<{ detail: string }>("/auth/logout", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      clearAuthTokens();
      router.push("/login");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Unable to log out");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>InvoiceFlow</h1>
      <p>You are signed in.</p>
      {error ? <p role="alert">{error}</p> : null}
      <button type="button" onClick={onLogout} disabled={loading}>
        {loading ? "Signing out..." : "Sign out"}
      </button>
    </main>
  );
}
