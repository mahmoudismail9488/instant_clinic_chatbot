import { useEffect, useRef, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ChevronDown,
  LayoutDashboard,
  Loader2,
  MessageSquarePlus,
  SendHorizontal,
  Trash2,
} from "lucide-react";
import { AnswerCard, RefusalCard, UserMessage } from "@/components/clinirag/AnswerCard";
import { EvidencePanel } from "@/components/clinirag/EvidencePanel";
import { GuardrailIndicator } from "@/components/clinirag/primitives";
import { pipelineStages, sectionFocusOptions, topics, type SectionFocusId, type Turn } from "@/lib/clinirag-data";
import { apiBaseUrl, queryGuidelines } from "@/lib/clinirag-api";
import {
  deleteChatSession,
  listChatSessions,
  saveChatSession,
  type ChatSession,
} from "@/lib/chat-history";
import { SignOutButton } from "@/components/clinirag/SignOutButton";
import { ThemeToggle } from "@/components/clinirag/ThemeToggle";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

type WorkspaceSearch = { topic?: string };

export const Route = createFileRoute("/_authenticated/workspace")({
  validateSearch: (search: Record<string, unknown>): WorkspaceSearch =>
    typeof search["topic"] === "string" ? { topic: search["topic"] } : {},
  head: () => ({
    meta: [
      { title: "Query Workspace — GlucoRAG" },
      {
        name: "description",
        content:
          "Ask guideline questions with citations, evidence scores, and saved chat history.",
      },
    ],
  }),
  component: Workspace,
});

function Workspace() {
  const { topic } = Route.useSearch();
  const { user } = useAuth();
  const scope = topics.find((t) => t.id === topic) ?? topics[0]!;
  const [turns, setTurns] = useState<Turn[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatSession[]>([]);
  const [activeChunk, setActiveChunk] = useState<string | null>(null);
  const [pipelineOpen, setPipelineOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(true);
  const [draft, setDraft] = useState("");
  const [sectionFocus, setSectionFocus] = useState<SectionFocusId>("any");
  const [mobileTab, setMobileTab] = useState<"chat" | "evidence" | "history">("chat");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);

  const current = turns[turns.length - 1];

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, loading]);

  useEffect(() => {
    if (!user?.id) return;
    void listChatSessions(user.id).then(setHistory);
  }, [user?.id]);

  async function persist(nextTurns: Turn[], id: string | null) {
    if (!user?.id || nextTurns.length === 0) return;
    const saved = await saveChatSession(user.id, {
      id,
      topic: scope.id,
      turns: nextTurns,
    });
    setSessionId(saved.id);
    setHistory((prev) => {
      const rest = prev.filter((s) => s.id !== saved.id);
      return [saved, ...rest];
    });
  }

  function startNewChat() {
    setTurns([]);
    setSessionId(null);
    setActiveChunk(null);
    setError(null);
    setMobileTab("chat");
  }

  function loadSession(session: ChatSession) {
    setTurns(session.turns);
    setSessionId(session.id);
    setActiveChunk(session.turns.at(-1)?.chunks[0]?.id ?? null);
    setError(null);
    setMobileTab("chat");
  }

  async function removeSession(id: string) {
    if (!user?.id) return;
    await deleteChatSession(user.id, id);
    setHistory((prev) => prev.filter((s) => s.id !== id));
    if (sessionId === id) startNewChat();
  }

  function onCitation(chunkId: string) {
    setActiveChunk(chunkId);
    setMobileTab("evidence");
    requestAnimationFrame(() => {
      document.getElementById(`chunk-${chunkId}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  async function send(preset?: string) {
    const question = (preset ?? draft).trim();
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
        sectionFocus,
        signal: ac.signal,
      });
      const next = [...turns, turn];
      setTurns(next);
      if (turn.chunks[0]) setActiveChunk(turn.chunks[0].id);
      await persist(next, sessionId);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      const message = err instanceof Error ? err.message : "Request failed";
      setError(
        message.includes("Failed to fetch")
          ? `Cannot reach API at ${apiBaseUrl()}. Start it with: uv run clinic-api`
          : message,
      );
    } finally {
      setLoading(false);
    }
  }

  const examples = [
    "Who should be screened for type 2 diabetes?",
    "Do I have diabetes?",
    "What medicine should I take?",
  ];

  const historyList = (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-3 py-2.5">
        <h2 className="text-[13px] font-semibold text-foreground">Saved chats</h2>
        <button
          type="button"
          onClick={startNewChat}
          className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-1 font-mono text-[11px] text-foreground hover:border-primary/50"
        >
          <MessageSquarePlus className="size-3.5" strokeWidth={1.5} />
          New
        </button>
      </div>
      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {history.length === 0 ? (
          <p className="px-2 py-4 text-[12px] text-muted-foreground">
            Chats save to your account after each answer (Supabase if configured, otherwise this browser).
          </p>
        ) : (
          history.map((s) => (
            <div
              key={s.id}
              className={cn(
                "group flex items-start gap-1 rounded-lg border border-transparent px-2 py-2 hover:border-border hover:bg-card",
                sessionId === s.id && "border-border bg-card",
              )}
            >
              <button
                type="button"
                onClick={() => loadSession(s)}
                className="min-w-0 flex-1 text-left"
              >
                <p className="truncate text-[13px] text-foreground">{s.title}</p>
                <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">
                  {new Date(s.updatedAt).toLocaleString()} · {s.turns.length} turn
                  {s.turns.length === 1 ? "" : "s"}
                </p>
              </button>
              <button
                type="button"
                title="Delete chat"
                onClick={() => void removeSession(s.id)}
                className="rounded p-1 text-muted-foreground opacity-70 hover:bg-secondary hover:text-destructive group-hover:opacity-100"
              >
                <Trash2 className="size-3.5" strokeWidth={1.5} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="flex h-screen flex-col bg-background">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-card px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] uppercase tracking-wide text-primary">GlucoRAG</span>
          <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[13px] text-foreground">
            {scope.title}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-[13px] text-foreground hover:border-primary/50"
          >
            <LayoutDashboard className="size-3.5" strokeWidth={1.5} />
            Pipeline
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
        {(["history", "chat", "evidence"] as const).map((t) => (
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
        <aside
          className={cn(
            "min-h-0 w-full border-r border-border bg-background md:block md:w-[220px] md:shrink-0",
            mobileTab === "history" ? "block" : "hidden md:block",
            !historyOpen && "md:hidden",
          )}
        >
          {historyList}
        </aside>

        <section
          className={cn(
            "min-h-0 flex-1 flex-col md:flex",
            mobileTab === "chat" ? "flex" : "hidden",
          )}
        >
          <div ref={listRef} className="flex-1 space-y-5 overflow-y-auto p-4">
            {turns.length === 0 && !loading && (
              <div className="rounded-xl border border-dashed border-border bg-card px-4 py-8 text-center">
                <p className="text-[15px] font-medium text-foreground">Ask a guideline question</p>
                <p className="mx-auto mt-1.5 max-w-md text-[13px] leading-relaxed text-muted-foreground">
                  Grounded in Diabetes Canada CPG + NICE NG28. Your account keeps prior chats in the sidebar.
                </p>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {examples.map((q) => (
                    <button
                      key={q}
                      type="button"
                      disabled={loading}
                      onClick={() => void send(q)}
                      className="rounded-full border border-border bg-background px-3 py-1.5 text-left text-[12px] text-foreground transition-colors hover:border-primary/50 hover:bg-secondary disabled:opacity-50"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
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
                Retrieving guidelines and generating a grounded answer…
              </div>
            )}
            {error && (
              <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-[13px] text-destructive">
                {error}
              </p>
            )}
          </div>
          <div className="border-t border-border bg-card p-3">
            <div className="mb-2 flex flex-wrap gap-1.5">
              {sectionFocusOptions.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  disabled={loading}
                  onClick={() => setSectionFocus(opt.id)}
                  className={cn(
                    "rounded-md border px-2.5 py-1 text-[12px] transition-colors disabled:opacity-50",
                    sectionFocus === opt.id
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:border-primary/40 hover:text-foreground",
                  )}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && void send()}
                placeholder="Ask a guideline question…"
                disabled={loading}
                className="h-11 flex-1 rounded-xl border border-border bg-background px-3.5 text-[15px] text-foreground outline-none placeholder:text-muted-foreground focus:border-primary disabled:opacity-60"
              />
              <button
                type="button"
                onClick={() => void send()}
                disabled={loading || !draft.trim()}
                className="inline-flex h-11 items-center gap-1.5 rounded-xl bg-primary px-4 text-[14px] font-medium text-primary-foreground transition-colors duration-150 hover:bg-primary-hover disabled:opacity-40"
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
              <button
                type="button"
                className="hidden font-mono text-[11px] text-muted-foreground hover:text-foreground md:inline"
                onClick={() => setHistoryOpen((v) => !v)}
              >
                {historyOpen ? "Hide history" : "Show history"}
              </button>
            </div>
          </div>
        </section>

        <aside
          className={cn(
            "min-h-0 border-l border-border bg-background md:block md:basis-[32%]",
            mobileTab === "evidence" ? "block flex-1" : "hidden",
          )}
        >
          <EvidencePanel chunks={current?.chunks ?? []} activeChunk={activeChunk} judgeMode />
        </aside>
      </div>
    </div>
  );
}
