import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowRight, FileText, Lock, Plus, ShieldCheck } from "lucide-react";
import { topics } from "@/lib/clinirag-data";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CliniRAG — Evidence-Grounded Clinical Guideline Assistant" },
      {
        name: "description",
        content:
          "CliniRAG answers clinical guideline questions with citations to WHO, CDC, NICE and USPSTF source text — and refuses when evidence is insufficient.",
      },
      { property: "og:title", content: "CliniRAG — Evidence-Grounded Clinical Assistant" },
      {
        property: "og:description",
        content: "Every answer cited to official guideline text. Fluent answer ≠ safe answer.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  const [selected, setSelected] = useState<string | null>(null);
  const navigate = useNavigate();
  const topic = topics.find((t) => t.id === selected);
  const { session, loading } = useAuth();

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-16">
      <div className="w-full max-w-[640px]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="font-mono text-[12px] uppercase tracking-wide text-primary">
            CliniRAG · Evidence-Grounded Clinical Assistant
          </p>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            {!loading &&
              (session ? (
                <>
                <Link
                  to="/workspace"
                  className="rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
                >
                  Open workspace
                </Link>
                <SignOutButton />
                </>
              ) : (
              <Link
                to="/auth"
                className="rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
              >
                Sign in
              </Link>
              ))}
          </div>
        </div>
        <h1 className="mt-3 text-[36px] font-semibold leading-tight text-foreground">
          Ask questions grounded in official guidelines.
        </h1>
        <p className="mt-3 text-[16px] text-muted-foreground">
          Every answer is cited to WHO, CDC, NICE, or USPSTF source text. No private data. No
          unsupported claims.
        </p>

        <div className="mt-8 rounded-xl border border-border bg-card p-5">
          <h2 className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
            Select clinical scope
          </h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {topics.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setSelected(t.id)}
                className={cn(
                  "rounded-xl border border-border p-4 text-left transition-colors duration-150 hover:border-primary/50",
                  selected === t.id && "border-primary bg-secondary",
                )}
              >
                <span className="block text-[16px] font-semibold text-foreground">{t.title}</span>
                <span className="mt-1 block text-[14px] text-muted-foreground">{t.blurb}</span>
              </button>
            ))}
            <div className="flex items-center gap-2 rounded-xl border border-dashed border-border p-4 text-[14px] text-muted-foreground">
              <Plus className="size-4" strokeWidth={1.5} />
              Add topic
              <span className="font-mono text-[12px]">(roadmap)</span>
            </div>
          </div>

          {topic && (
            <div className="mt-4 border-t border-border pt-4">
              <p className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
                Ingested sources for this scope
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {topic.sources.map((s) => (
                  <span
                    key={s}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border bg-background px-2 py-1 font-mono text-[12px] text-foreground"
                  >
                    <FileText className="size-3" strokeWidth={1.5} />
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            type="button"
            disabled={!topic}
            onClick={() =>
              session
                ? navigate({ to: "/workspace", search: { topic: topic!.id } })
                : navigate({ to: "/auth", search: { redirect: `/workspace?topic=${topic!.id}` } })
            }
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[15px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-40"
          >
            {session ? "Start session" : "Sign in to start session"}
            <ArrowRight className="size-4" strokeWidth={1.5} />
          </button>
        </div>

        <p className="mt-5 flex items-center gap-2 text-[12px] text-muted-foreground">
          <ShieldCheck className="size-3.5" strokeWidth={1.5} />
          Fluent answer ≠ safe answer. CliniRAG will visibly refuse out-of-scope or unsupported
          questions.
        </p>
        <p className="mt-2 flex items-center gap-2 text-[12px] text-muted-foreground">
          <Lock className="size-3.5" strokeWidth={1.5} />
          Clinicians cannot upload files. Only administrators curate the guideline corpus.
        </p>
      </div>
    </main>
  );
}