import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronDown, LayoutDashboard, SendHorizontal } from "lucide-react";
import { AnswerCard, RefusalCard, UserMessage } from "@/components/clinirag/AnswerCard";
import { EvidencePanel } from "@/components/clinirag/EvidencePanel";
import { GuardrailIndicator } from "@/components/clinirag/primitives";
import { demoTurns, pipelineStages, topics } from "@/lib/clinirag-data";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";
import { cn } from "@/lib/utils";

type WorkspaceSearch = { topic?: string };

export const Route = createFileRoute("/_authenticated/workspace")({
  validateSearch: (search: Record<string, unknown>): WorkspaceSearch =>
    typeof search["topic"] === "string" ? { topic: search["topic"] } : {},
  head: () => ({
    meta: [
      { title: "Query Workspace — CliniRAG" },
      {
        name: "description",
        content:
          "Ask guideline questions and read the retrieved evidence chunks, similarity scores and citations side by side.",
      },
      { property: "og:title", content: "Query Workspace — CliniRAG" },
      {
        property: "og:description",
        content: "Structured answer cards with citation chips and a live evidence panel.",
      },
    ],
  }),
  component: Workspace,
});

function Workspace() {
  const { topic } = Route.useSearch();
  const scope = topics.find((t) => t.id === topic) ?? topics[0]!;
  const [visible, setVisible] = useState(1);
  const [activeChunk, setActiveChunk] = useState<string | null>(null);
  const [pipelineOpen, setPipelineOpen] = useState(true);
  const [draft, setDraft] = useState("");
  const [mobileTab, setMobileTab] = useState<"chat" | "evidence">("chat");

  const turns = demoTurns.slice(0, visible);
  const current = turns[turns.length - 1]!;

  function onCitation(chunkId: string) {
    setActiveChunk(chunkId);
    setMobileTab("evidence");
    requestAnimationFrame(() => {
      document.getElementById(`chunk-${chunkId}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function send() {
    setDraft("");
    setActiveChunk(null);
    setVisible((v) => Math.min(v + 1, demoTurns.length));
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-card px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] uppercase tracking-wide text-primary">CliniRAG</span>
          <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[13px] text-foreground">
            {scope.title}
          </span>
          <Link to="/" className="text-[13px] text-primary hover:text-primary-hover">
            change topic
          </Link>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
          >
            <LayoutDashboard className="size-3.5" strokeWidth={1.5} />
            Judge view
          </Link>
          <ThemeToggle />
          <SignOutButton />
        </div>
      </header>

      <div className="border-b border-border bg-card px-4 pb-2">
        <button
          type="button"
          onClick={() => setPipelineOpen((v) => !v)}
          className="flex items-center gap-1 font-mono text-[12px] text-muted-foreground"
        >
          Pipeline status
          <ChevronDown className={cn("size-3.5 transition-transform", !pipelineOpen && "-rotate-90")} />
        </button>
        {pipelineOpen && (
          <div className="flex flex-wrap gap-x-3 gap-y-1 pt-1 font-mono text-[12px] text-muted-foreground">
            {pipelineStages.slice(0, 4).map((s) => (
              <span key={s.name}>
                {s.name} <span className="text-confidence-high">✓</span>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="flex border-b border-border bg-card md:hidden">
        {(["chat", "evidence"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setMobileTab(t)}
            className={cn(
              "flex-1 py-2 text-[13px] capitalize",
              mobileTab === t ? "border-b-2 border-primary text-primary" : "text-muted-foreground",
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex min-h-0 flex-1">
        <section
          className={cn(
            "min-h-0 flex-1 flex-col md:flex md:basis-[65%]",
            mobileTab === "chat" ? "flex" : "hidden",
          )}
        >
          <div className="flex-1 space-y-5 overflow-y-auto p-4">
            {turns.map((turn) => (
              <div key={turn.id} className="space-y-3">
                <UserMessage text={turn.question} />
                {turn.kind === "answer" ? (
                  <AnswerCard turn={turn} onCitation={onCitation} activeChunk={activeChunk} />
                ) : (
                  <RefusalCard turn={turn} />
                )}
              </div>
            ))}
          </div>
          <div className="border-t border-border bg-card p-3">
            <div className="flex items-center gap-2">
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder={
                  visible < demoTurns.length
                    ? "Ask a guideline question…"
                    : "Demo session complete — reload to restart"
                }
                className="h-10 flex-1 rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
              />
              <button
                type="button"
                onClick={send}
                disabled={visible >= demoTurns.length}
                className="inline-flex h-10 items-center gap-1.5 rounded-lg bg-primary px-3.5 text-[14px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:opacity-40"
              >
                <SendHorizontal className="size-4" strokeWidth={1.5} />
                Send
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <GuardrailIndicator />
              <span className="font-mono text-[12px] text-muted-foreground">
                Scope locked · {scope.sources.length} source documents
              </span>
            </div>
          </div>
        </section>

        <aside
          className={cn(
            "min-h-0 border-l border-border bg-background md:block md:basis-[35%]",
            mobileTab === "evidence" ? "block flex-1" : "hidden",
          )}
        >
          <EvidencePanel chunks={current.chunks} activeChunk={activeChunk} judgeMode />
        </aside>
      </div>
    </div>
  );
}