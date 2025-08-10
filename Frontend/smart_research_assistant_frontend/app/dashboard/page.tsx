"use client";

import { useEffect, useState, useRef } from "react";
import { supabase } from "@/app/core/supabase/client";
import { useRouter } from "next/navigation";
import { BrainCircuit, Loader, Menu, Paperclip, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import clsx from "clsx";
import { X } from "lucide-react";
import { email } from "zod";

export default function DashboardPage() {
  const router = useRouter();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    const getUser = async () => {
      const { data, error } = await supabase.auth.getUser();
      if (data?.user) {
        setUserEmail(data.user.email ?? null);
      } else {
        router.replace("/sign-in");
      }
    };
    getUser();
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.replace("/sign-in");
  };

  const handlePdfSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") {
      setPdfFile(file);
    }
  };

  const handleSend = async () => {
    if (!message && !pdfFile) return;
    setLoading(true);
    try {
      // Upload PDF if available
      if (pdfFile) {
        const formData = new FormData();
        formData.append("file", pdfFile);
        formData.append("email", userEmail ?? "");

        const uploadRes = await fetch(
          "http://127.0.0.1:8000/api/upload-file/",
          {
            method: "POST",
            body: formData,
          }
        );

        if (!uploadRes.ok) {
          throw new Error("Failed to upload PDF");
        }
        setMessages((prev) => [
          ...prev,
          {
            role: "user",
            content: `📄 ${pdfFile.name} has been uploaded and processed. You can start querying now.`,
          },
        ]);
        setPdfFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }

      // Send query message if available
      if (message) {
        setMessages((prev) => [
          ...prev,
          {
            role: "user",
            content: message,
          },
        ]);
        const queryRes = await fetch("http://127.0.0.1:8000/api/search/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query: message, email: userEmail }),
        });

        if (!queryRes.ok) {
          throw new Error("Failed to send message");
        }
        const response = await queryRes.json();
        console.log(response);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: response.answer?.content || String(response.answer),
          },
        ]);
        setMessage("");
      }

      // Optionally show message in UI
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-[#4a2574] to-[#0f0529] text-white">
      {/* Hamburger menu */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="md:hidden absolute top-4 left-4 z-50 p-2 rounded-md bg-white/10 hover:bg-white/20"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Sidebar */}
      <aside
        className={clsx(
          "fixed md:static z-40 top-0 left-0 h-full w-[250px] bg-[#1f0c38] p-4 border-r border-white/10 flex flex-col justify-between transition-transform duration-300 ease-in-out",
          {
            "-translate-x-full": !sidebarOpen,
            "translate-x-0": sidebarOpen,
            "md:translate-x-0": true,
          }
        )}
      >
        <div>
          <h2 className="text-xl font-bold mb-6">Smart Assistant</h2>
          <ul className="space-y-2 text-white/80">
            <li className="hover:text-white cursor-pointer">New Chat</li>
            <li className="hover:text-white cursor-pointer">History</li>
          </ul>
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
          className="text-sm text-white hover:bg-white/10"
        >
          Sign Out
        </Button>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 md:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Chat UI */}
      <main className="flex flex-col flex-1 h-full relative">
        {/* Chat area */}
        <div
          className={clsx(
            "flex-1 overflow-y-auto p-6 space-y-4",
            messages.length === 0 ? "flex items-center justify-center" : ""
          )}
        >
          {messages.length === 0 ? (
            <div className="text-center text-white/80 italic max-w-[70%]">
              Hello {userEmail}, how can I help you today?
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={clsx(
                    "p-3 rounded-xl max-w-[70%]",
                    msg.role === "assistant"
                      ? "self-end bg-[#F8B55F] text-[#4a2574]"
                      : "self-end bg-white/10 text-white/80 italic"
                  )}
                >
                  {msg.content}
                </div>
              ))}
            </>
          )}
        </div>

        {/* Input area */}
        <div className="w-full p-4 border-t border-white/10 bg-[#1f0c38]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex flex-col md:flex-row items-center gap-3"
          >
            <div className="flex-1 w-full">
              <Input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="bg-white/10 text-white placeholder:text-white/50"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <Label
                htmlFor="pdf-upload"
                className="cursor-pointer flex items-center gap-1 text-sm text-white/80 hover:text-white"
              >
                <Paperclip className="w-4 h-4" />
                Attach PDF
              </Label>
              <Input
                id="pdf-upload"
                type="file"
                accept="application/pdf"
                className="hidden"
                ref={fileInputRef}
                onChange={handlePdfSelect}
              />
              <Button
                type="submit"
                className="bg-[#F8B55F] text-[#4a2574] hover:bg-white"
              >
                {loading ? (
                  <Loader />
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-1" />
                    Send
                  </>
                )}
              </Button>
            </div>
          </form>

          {pdfFile && (
            <div className="mt-3 flex items-center justify-between bg-white/10 p-2 rounded-md text-sm text-white/80">
              <div className="truncate">
                📄 <strong>{pdfFile.name}</strong> (
                {(pdfFile.size / 1024).toFixed(1)} KB)
              </div>
              <button
                type="button"
                onClick={() => {
                  setPdfFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
                className="ml-4 text-red-400 hover:text-red-200 text-xs"
              >
                <X className="w-4 h-4 ml-2 text-red-400 hover:text-red-200 cursor-pointer" />
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
