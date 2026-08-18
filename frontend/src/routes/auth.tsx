import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Loader2, ShieldCheck } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { lovable } from "@/integrations/lovable/index";
import { useAuth } from "@/hooks/use-auth";

type AuthSearch = { redirect?: string };

export const Route = createFileRoute("/auth")({
  validateSearch: (search: Record<string, unknown>): AuthSearch =>
    typeof search["redirect"] === "string" ? { redirect: search["redirect"] } : {},
  head: () => ({
    meta: [
      { title: "Sign in — CliniRAG Clinical Assistant" },
      {
        name: "description",
        content:
          "Sign in to CliniRAG with email or Google to query evidence-grounded clinical guideline answers.",
      },
      { property: "og:title", content: "Sign in — CliniRAG" },
      {
        property: "og:description",
        content: "Email or Google sign-in for the evidence-grounded clinical guideline assistant.",
      },
    ],
  }),
  component: AuthPage,
});

function safePath(value: string | undefined) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/workspace";
  if (value.startsWith("/auth")) return "/workspace";
  return value;
}

function AuthPage() {
  const { redirect } = Route.useSearch();
  const { session, loading } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const target = safePath(redirect);

  useEffect(() => {
    if (!loading && session) navigate({ to: target, replace: true });
  }, [loading, session, navigate, target]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setMessage(null);
    if (mode === "signup") {
      const { data, error: err } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: window.location.origin },
      });
      if (err) setError(err.message);
      else if (!data.session) setMessage("Check your email to confirm your account, then sign in.");
    } else {
      const { error: err } = await supabase.auth.signInWithPassword({ email, password });
      if (err) setError(err.message);
    }
    setBusy(false);
  }

  async function google() {
    setError(null);
    setBusy(true);
    const result = await lovable.auth.signInWithOAuth("google", {
      redirect_uri: window.location.origin,
    });
    if (result.error) {
      setError("Google sign-in failed. Please try again.");
      setBusy(false);
      return;
    }
    if (result.redirected) return;
    navigate({ to: target, replace: true });
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-16">
      <div className="w-full max-w-[420px]">
        <p className="font-mono text-[12px] uppercase tracking-wide text-primary">CliniRAG · Access</p>
        <h1 className="mt-3 text-[28px] font-semibold leading-tight text-foreground">
          {mode === "signin" ? "Sign in to your workspace" : "Create your clinician account"}
        </h1>
        <p className="mt-2 text-[14px] text-muted-foreground">
          Guideline documents are curated by administrators. Clinicians query — they never upload.
        </p>

        <div className="mt-6 rounded-xl border border-border bg-card p-5">
          <button
            type="button"
            onClick={google}
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2.5 text-[15px] font-medium text-foreground transition-colors hover:border-primary/50 disabled:opacity-50"
          >
            Continue with Google
          </button>

          <div className="my-4 flex items-center gap-3">
            <span className="h-px flex-1 bg-border" />
            <span className="font-mono text-[12px] uppercase text-muted-foreground">or email</span>
            <span className="h-px flex-1 bg-border" />
          </div>

          <form onSubmit={submit} className="space-y-3">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="clinician@hospital.org"
              className="h-10 w-full rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
            />
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="h-10 w-full rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
            />
            <button
              type="submit"
              disabled={busy}
              className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 text-[15px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
            >
              {busy && <Loader2 className="size-4 animate-spin" strokeWidth={1.5} />}
              {mode === "signin" ? "Sign in" : "Create account"}
            </button>
          </form>

          {error && (
            <p className="mt-3 rounded-lg border border-confidence-insufficient/30 bg-safety-refuse-bg px-3 py-2 text-[13px] text-confidence-insufficient">
              {error}
            </p>
          )}
          {message && (
            <p className="mt-3 rounded-lg border border-border bg-secondary px-3 py-2 text-[13px] text-foreground">
              {message}
            </p>
          )}

          <button
            type="button"
            onClick={() => {
              setMode(mode === "signin" ? "signup" : "signin");
              setError(null);
              setMessage(null);
            }}
            className="mt-4 text-[13px] text-primary hover:text-primary-hover"
          >
            {mode === "signin" ? "No account? Create one" : "Already registered? Sign in"}
          </button>
        </div>

        <p className="mt-5 flex items-center gap-2 text-[12px] text-muted-foreground">
          <ShieldCheck className="size-3.5" strokeWidth={1.5} />
          File uploads are restricted to administrators. No patient data is stored.
        </p>
      </div>
    </main>
  );
}