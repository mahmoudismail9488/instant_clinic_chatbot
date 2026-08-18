import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { evalRows, guardrailLog, pipelineStages } from "@/lib/clinirag-data";
import { AdminDocuments } from "@/components/clinirag/AdminDocuments";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/_authenticated/dashboard")({
  head: () => ({
    meta: [
      { title: "Judge Dashboard — CliniRAG Pipeline & Evaluation" },
      {
        name: "description",
        content:
          "Retrieval Precision@K, citation accuracy, faithfulness rate, the 7-stage RAG pipeline, evaluation table and live guardrail log.",
      },
      { property: "og:title", content: "Judge Dashboard — CliniRAG" },
      {
        property: "og:description",
        content: "Retrieval, grounding, architecture, evaluation and safety metrics in one view.",
      },
    ],
  }),
  component: Dashboard,
});

const stats = [
  { label: "Retrieval Precision@5", value: "0.82", sub: "+0.06 vs baseline", spark: [58, 62, 66, 71, 74, 79, 82] },
  { label: "Citation Accuracy", value: "94%", sub: "47 of 50 citations verified", spark: [80, 84, 86, 88, 90, 92, 94] },
  { label: "Unsupported Claim Rate", value: "3.1%", sub: "lower is better", spark: [12, 10, 9, 7, 6, 4, 3] },
];

function Sparkline({ points }: { points: number[] }) {
  const max = Math.max(...points);
  const d = points
    .map((p, i) => `${(i / (points.length - 1)) * 100},${30 - (p / max) * 28}`)
    .join(" ");
  return (
    <svg viewBox="0 0 100 30" preserveAspectRatio="none" className="mt-3 h-8 w-full">
      <polyline points={d} fill="none" stroke="var(--color-primary)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

function Dashboard() {
  const [stage, setStage] = useState(0);
  const { user } = useAuth();

  return (
    <main className="min-h-screen bg-background">
      <header className="flex items-center justify-between border-b border-border bg-card px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] uppercase tracking-wide text-primary">CliniRAG</span>
          <span className="text-[14px] font-semibold text-foreground">Judge view</span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/workspace"
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
          >
            <ArrowLeft className="size-3.5" strokeWidth={1.5} />
            Back to workspace
          </Link>
          <ThemeToggle />
          <SignOutButton />
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-6">
        <AdminDocuments userId={user?.id} />
        <section className="grid gap-4 md:grid-cols-3">
          {stats.map((s) => (
            <div key={s.label} className="rounded-xl border border-border bg-card p-4">
              <p className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">{s.label}</p>
              <p className="mt-1 font-mono text-[36px] leading-tight text-foreground">{s.value}</p>
              <p className="text-[13px] text-muted-foreground">{s.sub}</p>
              <Sparkline points={s.spark} />
            </div>
          ))}
        </section>

        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="text-[14px] font-semibold text-foreground">Pipeline architecture</h2>
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

        <section className="rounded-xl border border-border bg-card">
          <h2 className="border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground">
            Evaluation set · 10 of 20 labeled questions
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[13px]">
              <thead className="font-mono text-[12px] uppercase text-muted-foreground">
                <tr className="border-b border-border">
                  <th className="px-4 py-2 font-normal">Question</th>
                  <th className="px-4 py-2 font-normal">Expected chunk</th>
                  <th className="px-4 py-2 font-normal">Retrieved@5</th>
                  <th className="px-4 py-2 font-normal">Match</th>
                  <th className="px-4 py-2 font-normal">Citation</th>
                  <th className="px-4 py-2 font-normal">Notes</th>
                </tr>
              </thead>
              <tbody>
                {evalRows.map((r) => (
                  <tr key={r.q} className="border-b border-border last:border-0">
                    <td className="px-4 py-2 text-foreground">{r.q}</td>
                    <td className="px-4 py-2 font-mono text-[12px] text-muted-foreground">{r.expected}</td>
                    <td className="px-4 py-2 font-mono text-[12px] text-muted-foreground">{r.retrieved}</td>
                    <td className={cn("px-4 py-2 font-mono", r.match ? "text-confidence-high" : "text-confidence-low")}>
                      {r.match ? "✓" : "✗"}
                    </td>
                    <td className={cn("px-4 py-2 font-mono", r.citation ? "text-confidence-high" : "text-confidence-low")}>
                      {r.citation ? "✓" : "✗"}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground">{r.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-border bg-card">
          <h2 className="border-b border-border px-4 py-3 text-[14px] font-semibold text-foreground">
            Guardrail log · last 6 queries
          </h2>
          <table className="w-full text-left text-[13px]">
            <tbody>
              {guardrailLog.map((g) => (
                <tr key={g.time} className="border-b border-border last:border-0">
                  <td className="px-4 py-2 font-mono text-[12px] text-muted-foreground">{g.time}</td>
                  <td className="px-4 py-2 text-foreground">{g.query}</td>
                  <td className="px-4 py-2 text-right">
                    <span
                      className={cn(
                        "rounded-md border px-2 py-0.5 font-mono text-[12px]",
                        g.classification === "Allowed" &&
                          "border-confidence-high/30 bg-confidence-high/8 text-confidence-high",
                        g.classification === "Needs Caution" &&
                          "border-safety-caution/30 bg-safety-caution-bg text-safety-caution",
                        g.classification === "Refuse" &&
                          "border-confidence-insufficient/30 bg-safety-refuse-bg text-confidence-insufficient",
                      )}
                    >
                      {g.classification}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </main>
  );
}