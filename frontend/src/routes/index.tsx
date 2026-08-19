import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowRight, FileText, ShieldCheck } from "lucide-react";
import { topics } from "@/lib/clinirag-data";
import { useAuth } from "@/hooks/use-auth";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "GlucoRAG — Guideline-Grounded Diabetes Assistant" },
      {
        name: "description",
        content:
          "Ask diabetes screening and adult type 2 guideline questions with citations to Diabetes Canada and NICE NG28.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  const navigate = useNavigate();
  const { session, loading } = useAuth();
  const topic = topics[0]!;

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-16">
      <div className="w-full max-w-[640px]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="font-mono text-[12px] uppercase tracking-wide text-primary">GlucoRAG</p>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            {!loading &&
              (session ? (
                <>
                  <Link
                    to="/workspace"
                    search={{ topic: topic.id }}
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

        <h1 className="mt-4 text-[36px] font-semibold leading-tight text-foreground">
          {topic.title}
        </h1>
        <p className="mt-3 text-[16px] leading-relaxed text-muted-foreground">{topic.blurb}</p>

        <div className="mt-8 rounded-xl border border-border bg-card p-5">
          <h2 className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
            Indexed sources
          </h2>
          <div className="mt-3 flex flex-wrap gap-2">
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

          <button
            type="button"
            onClick={() =>
              session
                ? navigate({ to: "/workspace", search: { topic: topic.id } })
                : navigate({
                    to: "/auth",
                    search: { redirect: `/workspace?topic=${topic.id}` },
                  })
            }
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[15px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover"
          >
            {session ? "Start session" : "Sign in to start"}
            <ArrowRight className="size-4" strokeWidth={1.5} />
          </button>
        </div>

        <p className="mt-5 flex items-start gap-2 text-[12px] text-muted-foreground">
          <ShieldCheck className="mt-0.5 size-3.5 shrink-0" strokeWidth={1.5} />
          Answers are citation-backed. The system refuses medication advice, personal diagnosis, and weak evidence.
        </p>
      </div>
    </main>
  );
}
