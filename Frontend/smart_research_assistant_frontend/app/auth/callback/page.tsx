"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/app/core/supabase/client";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const handleCallback = async () => {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (session) {
        router.replace("/dashboard"); // or home page
      } else {
        console.error("Login failed", error);
        router.replace("/sign-in"); // fallback if needed
      }
    };

    handleCallback();
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p>Logging you in...</p>
    </div>
  );
}
