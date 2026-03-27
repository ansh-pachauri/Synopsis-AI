"use client";

import { supabase } from "@/src/lib/subapase";
import { useRouter } from "next/navigation";

export default function LoginButton() {
  const router = useRouter();

  const handleLogin = async () => {
    const redirectTo = `${window.location.origin}/auth/callback`;
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo,
      },
    });

    if (error) {
      console.error("OAuth login failed", error);
      return;
    }

    if (!data.url) {
      router.push("/auth/callback");
    }
  };

  return (
    <div>
      <button
        className="text-black bg-white rounded-3xl p-4 m-4 w-auto h-14"
        onClick={handleLogin}
      >
        Google Login
      </button>
    </div>
  );
}
