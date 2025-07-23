"use client";

import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";

import { supabase } from "@/app/core/supabase/client"; // make sure this uses createBrowserClient()

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
const formSchema = z.object({
  email: z.string().email("Enter a valid email address."),
});

export default function SignInPage() {
  const [message, setMessage] = useState("");
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    const { error } = await supabase.auth.signInWithOtp({
      email: values.email,
      options: {
        emailRedirectTo: "http://localhost:3000/auth/callback",
      },
    });

    if (error) {
      setMessage("Something went wrong. Try again.");
      console.error(error.message);
    } else {
      setMessage("Magic link sent! Check your inbox.");
    }
  };
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
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in with Magic Link</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="you@example.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full">
                Send Magic Link
              </Button>
              {message && (
                <p className="text-sm text-muted-foreground text-center pt-2">
                  {message}
                </p>
              )}
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
