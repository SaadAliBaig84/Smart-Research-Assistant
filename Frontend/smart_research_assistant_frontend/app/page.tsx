"use client";
import { BrainCircuit } from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { supabase } from "@/app/core/supabase/client";
import { useEffect } from "react";
export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session) router.replace("/dashboard");
    };

    checkSession();
  }, [router]);
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#4a2574] to-[#0f0529] flex flex-col items-center justify-center text-white px-4">
      <div className="flex flex-col items-center space-y-6">
        <div className="relative flex items-center justify-center">
          {/* Wave */}
          <motion.div
            animate={{
              scale: [1, 1.5, 2],
              opacity: [0.3, 0.2, 0],
            }}
            transition={{
              duration: 1.5,
              ease: "easeOut",
              repeat: Infinity,
              repeatType: "loop",
              repeatDelay: 0, // Wait 0.5s after vanishing before restarting
            }}
            className="absolute w-[120px] h-[120px] bg-purple-400/30 rounded-full"
          />

          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{
              duration: 1.5,
              ease: "easeOut",
              repeat: Infinity,
              repeatType: "loop",
            }}
            className="relative z-10 p-4"
          >
            <BrainCircuit className="w-20 h-20 text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
          </motion.div>
        </div>
        <h1 className="text-5xl font-extrabold tracking-wide text-center drop-shadow-md">
          Smart Research Assistant
        </h1>
        <p className="text-lg text-center max-w-xl text-white/80">
          Your AI-powered tool for summarizing, translating, and understanding
          research articles with ease.
        </p>
        <button
          className="mt-6 px-6 py-3 bg-[#F8B55F] text-[#4a2574] font-semibold rounded-2xl shadow-md hover:bg-gray-100 transition"
          onClick={() => router.push("/sign-in")}
        >
          Get Started
        </button>
      </div>
    </div>
  );
}
