"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/src/lib/subapase";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [status, setStatus] = useState("Completing login...");

  useEffect(() => {
    const completeLogin = async () => {
      const url = new URL(window.location.href);
      const code = url.searchParams.get("code");
      const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
      const accessToken = hashParams.get("access_token");
      const refreshToken = hashParams.get("refresh_token");

      if (code) {
        const { error } = await supabase.auth.exchangeCodeForSession(code);

        if (error) {
          setStatus(error.message);
          return;
        }

        router.replace("/dashboard");
        return;
      }

      if (accessToken && refreshToken) {
        const { error } = await supabase.auth.setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
        });

        if (error) {
          setStatus(error.message);
          return;
        }

        router.replace("/dashboard");
        return;
      }

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (session?.access_token) {
        router.replace("/dashboard");
        return;
      }

      setStatus("Login session was not created. Redirecting to home...");
      router.replace("/");
    };

    void completeLogin();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
      <p className="text-center text-lg">{status}</p>
    </main>
  );
}
