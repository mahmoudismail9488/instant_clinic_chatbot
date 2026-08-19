import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { liveMetrics, pipelineStages, topics } from "@/lib/clinirag-data";
import { AdminDocuments } from "@/components/clinirag/AdminDocuments";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/_authenticated/dashboard")({
  head: () => ({
    meta: [
      { title: "GlucoRAG — Pipeline & corpus" },
      {
        name: "description",
        content: "Live metrics, pipeline stages, indexed sources, and admin corpus upload.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const [stage, setStage] = useState(0);
  const { user } = useAuth();
  const topic = topics[0]!;

  return (
    <main className="min-h-screen bg-background">
      <header className="flex items-center justify-between border-b border-border bg-card px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] uppercase tracking-wide text-primary">GlucoRAG</span>
          <span className="text-[14px] font-semibold text-foreground">Pipeline & corpus</span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/workspace"
            search={{ topic: topic.id }}
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
          >
            <ArrowLeft className="size-3.5" strokeWidth={1.5} />
            Workspace
          </Link>
          <ThemeToggle />
          <SignOutButton />
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="text-[14px] font-semibold text-foreground">What this page is for</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[13px] text-muted-foreground">
            <li>See live retrieval / Day 4 safety metrics from the lab reports</li>
            <li>Walk the production RAG pipeline stages</li>
            <li>Confirm which guideline PDFs are in scope</li>
            <li>Admins: upload additional guideline documents to Supabase storage</li>
          </ul>
        </section>

        <AdminDocuments userId={user?.id} />

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {liveMetrics.map((s) => (
            <div key={s.label} className="rounded-xl border border-border bg-card p-4">
              <p className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">{s.label}</p>
              <p className="mt-1 font-mono text-[32px] leading-tight text-foreground">{s.value}</p>
              <p className="mt-1 text-[13px] text-muted-foreground">{s.sub}</p>
            </div>
          ))}
        </section>

        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="text-[14px] font-semibold text-foreground">Pipeline</h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {pipelineStages.map((s, i) => (
              <div key={s.name} className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setStage(i)}
                  className={cn(
                    "rounded-lg border border-border px-2.5 py-1.5 text-[13px] transition-colors duration-150",
                    stage === i
                      ? "border-primary bg-secondary text-primary"
                      : "text-foreground hover:border-primary/50",
                  )}
                >
                  <span className="mr-1.5 font-mono text-[12px] text-muted-foreground">{i + 1}</span>
                  {s.name}
                </button>
                {i < pipelineStages.length - 1 && <span className="text-muted-foreground">→</span>}
              </div>
            ))}
          </div>
          <p className="mt-3 rounded-lg bg-secondary px-3 py-2 font-mono text-[12px] text-foreground">
            {pipelineStages[stage]!.name}: {pipelineStages[stage]!.metric}
          </p>
        </section>

        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="text-[14px] font-semibold text-foreground">Indexed corpus</h2>
          <p className="mt-1 text-[13px] text-muted-foreground">{topic.blurb}</p>
          <ul className="mt-3 space-y-2">
            {topic.sources.map((s) => (
              <li
                key={s}
                className="rounded-lg border border-border bg-background px-3 py-2 font-mono text-[12px] text-foreground"
              >
                {s}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
