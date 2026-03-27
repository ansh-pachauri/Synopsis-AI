import { supabase } from "../subapase";

export default async function SendTokenToBackend() {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("No active session. Please log in.");
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/protected`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    }
  );

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new Error(errorPayload?.detail || "Token verification failed.");
  }

  return response.json();
}
