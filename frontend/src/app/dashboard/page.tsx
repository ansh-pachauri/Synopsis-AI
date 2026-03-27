"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SendTokenToBackend from "@/src/lib/api/api";
import { supabase } from "@/src/lib/subapase";

type ProtectedResponse = {
  message: string;
  user_id?: string;
  token?: string;
  detail?: string;
};

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [backendResult, setBackendResult] = useState<ProtectedResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session?.access_token) {
        router.replace("/");
        return;
      }

      setToken(session.access_token);

      try {
        const response = await SendTokenToBackend();
        setBackendResult(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to verify token.");
      }
    };

    void loadSession();
  }, [router]);

  const handleLogout= async()=>{
    await supabase.auth.signOut();

    //redirect to home
    window.location.href = "/";
  }

  return (
    <main className="min-h-screen bg-black px-6 py-12 text-white">
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p>Google auth completed and the current Supabase access token is shown below.</p>
        <button
        className="text-black bg-white w-full rounded-2xl"
        onClick={handleLogout}>Logout</button>

        <section className="rounded-xl border border-white/20 p-4">
          <h2 className="mb-3 text-xl font-medium">Access Token</h2>
          <pre className="overflow-x-auto whitespace-pre-wrap break-all text-sm text-green-300">
            {token || "Loading token..."}
          </pre>
        </section>

        <section className="rounded-xl border border-white/20 p-4">
          <h2 className="mb-3 text-xl font-medium">Backend Verification</h2>
          {error ? (
            <p className="text-red-400">{error}</p>
          ) : (
            <pre className="overflow-x-auto whitespace-pre-wrap break-all text-sm text-blue-300">
              {backendResult ? JSON.stringify(backendResult, null, 2) : "Verifying token..."}
            </pre>
          )}
        </section>
      </div>
    </main>
  );
}
