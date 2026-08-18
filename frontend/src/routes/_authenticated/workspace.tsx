import { useEffect, useRef, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ChevronDown, LayoutDashboard, Loader2, SendHorizontal } from "lucide-react";
import { AnswerCard, RefusalCard, UserMessage } from "@/components/clinirag/AnswerCard";
import { EvidencePanel } from "@/components/clinirag/EvidencePanel";
import { GuardrailIndicator } from "@/components/clinirag/primitives";
import { pipelineStages, topics, type Turn } from "@/lib/clinirag-data";
import { apiBaseUrl, queryGuidelines } from "@/lib/clinirag-api";
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
  const scope = topics.find((t) => t.id === topic) ?? topics.find((t) => t.id === "diabetes") ?? topics[0]!;
  const [turns, setTurns] = useState<Turn[]>([]);
  const [activeChunk, setActiveChunk] = useState<string | null>(null);
  const [pipelineOpen, setPipelineOpen] = useState(true);
  const [draft, setDraft] = useState("");
  const [mobileTab, setMobileTab] = useState<"chat" | "evidence">("chat");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);

  const current = turns[turns.length - 1];

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, loading]);

  function onCitation(chunkId: string) {
    setActiveChunk(chunkId);
    setMobileTab("evidence");
    requestAnimationFrame(() => {
      document.getElementById(`chunk-${chunkId}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  async function send() {
    const question = draft.trim();
    if (!question || loading) return;

    setDraft("");
    setError(null);
    setActiveChunk(null);
    setLoading(true);
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;

    try {
      const turn = await queryGuidelines(question, {
        topic: scope.id,
        signal: ac.signal,
      });
      setTurns((prev) => [...prev, turn]);
      if (turn.chunks[0]) setActiveChunk(turn.chunks[0].id);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      const message =
        err instanceof Error
          ? err.message
          : "Request failed";
      setError(
        message.includes("Failed to fetch")
          ? `Cannot reach API at ${apiBaseUrl()}. Start it with: uv run clinic-api`
          : message,
      );
    } finally {
      setLoading(false);
    }
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
            <span className="text-muted-foreground/80">API {apiBaseUrl()}</span>
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
          <div ref={listRef} className="flex-1 space-y-5 overflow-y-auto p-4">
            {turns.length === 0 && !loading && (
              <p className="rounded-lg border border-dashed border-border bg-card px-4 py-6 text-center text-[14px] text-muted-foreground">
                Ask a guideline question grounded in the indexed corpus (Diabetes Canada CPG + NICE NG28).
                Example: “Who should be screened for type 2 diabetes?”
              </p>
            )}
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
            {loading && (
              <div className="flex items-center gap-2 text-[14px] text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                Retrieving guidelines and generating answer…
              </div>
            )}
            {error && (
              <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-[13px] text-destructive">
                {error}
              </p>
            )}
          </div>
          <div className="border-t border-border bg-card p-3">
            <div className="flex items-center gap-2">
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && void send()}
                placeholder="Ask a guideline question…"
                disabled={loading}
                className="h-10 flex-1 rounded-lg border border-border bg-background px-3 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary disabled:opacity-60"
              />
              <button
                type="button"
                onClick={() => void send()}
                disabled={loading || !draft.trim()}
                className="inline-flex h-10 items-center gap-1.5 rounded-lg bg-primary px-3.5 text-[14px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:opacity-40"
              >
                {loading ? (
                  <Loader2 className="size-4 animate-spin" strokeWidth={1.5} />
                ) : (
                  <SendHorizontal className="size-4" strokeWidth={1.5} />
                )}
                Send
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <GuardrailIndicator />
              <span className="font-mono text-[12px] text-muted-foreground">
                Live RAG · {scope.title}
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
          <EvidencePanel chunks={current?.chunks ?? []} activeChunk={activeChunk} judgeMode />
        </aside>
      </div>
    </div>
  );
}
