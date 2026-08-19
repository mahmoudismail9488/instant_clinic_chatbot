import { AlertTriangle, ShieldAlert } from "lucide-react";
import { Card, CitationChip, ConfidenceBadge } from "./primitives";
import type { AnswerTurn, RefusalTurn } from "@/lib/clinirag-data";

export function UserMessage({ text }: { text: string }) {
  return (
    <div className="flex justify-end animate-in fade-in slide-in-from-bottom-1 duration-200">
      <p className="max-w-[min(80%,42rem)] rounded-2xl bg-secondary px-3.5 py-2.5 text-[15px] leading-relaxed text-foreground shadow-sm">
        {text}
      </p>
    </div>
  );
}

export function AnswerCard({
  turn,
  onCitation,
  activeChunk,
}: {
  turn: AnswerTurn;
  onCitation: (chunkId: string) => void;
  activeChunk: string | null;
}) {
  return (
    <Card
      className={
        turn.caution
          ? "animate-in fade-in slide-in-from-bottom-1 duration-200 border-t-2 border-t-safety-caution"
          : "animate-in fade-in slide-in-from-bottom-1 duration-200"
      }
    >
      {turn.caution && (
        <div className="flex items-start gap-2 rounded-t-xl bg-safety-caution-bg px-4 py-2.5 text-[13px] text-safety-caution">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" strokeWidth={1.5} />
          <span>{turn.caution}</span>
        </div>
      )}
      <div className="flex flex-wrap items-start justify-between gap-3 px-4 pt-4">
        <div className="space-y-1.5">
          <h3 className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
            Recommendation
          </h3>
          <p className="font-mono text-[11px] text-muted-foreground">
            Status: <span className="text-foreground/80">{turn.status ?? "answered"}</span>
            <span className="mx-1.5 text-border">·</span>
            Evidence quality
          </p>
        </div>
        <ConfidenceBadge level={turn.confidence} score={turn.confidenceScore ?? null} />
      </div>
      <p className="whitespace-pre-wrap px-4 pt-3 text-[15px] leading-[1.65] text-foreground">
        {turn.recommendation}
      </p>

      <div className="px-4 pt-5">
        <h3 className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
          Supporting evidence
          <span className="ml-2 font-normal normal-case tracking-normal text-muted-foreground/80">
            {turn.evidence.length} claim{turn.evidence.length === 1 ? "" : "s"}
          </span>
        </h3>
      </div>
      <ul className="space-y-3 px-4 pt-2">
        {turn.evidence.map((e, i) => (
          <li
            key={`${e.citation.chunkId}-${i}`}
            className="rounded-lg border border-border/70 bg-background/50 px-3 py-2.5 text-[15px] leading-[1.6] text-foreground"
          >
            <span className="mr-2 font-mono text-[11px] text-muted-foreground">{i + 1}.</span>
            {e.text}
            <div className="mt-1.5">
              <CitationChip
                citation={e.citation}
                onSelect={onCitation}
                active={activeChunk === e.citation.chunkId}
              />
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-5 space-y-1 rounded-b-xl border-t border-border bg-muted/20 px-4 py-2.5 text-[12px] text-muted-foreground">
        <p>This supports — not replaces — clinical judgment. Confidence is evidence quality, not a diagnosis probability.</p>
        {turn.nextAction && (
          <p className="text-foreground/80">
            Suggested next action: {turn.nextAction}
          </p>
        )}
      </div>
    </Card>
  );
}

export function RefusalCard({ turn }: { turn: RefusalTurn }) {
  return (
    <Card className="animate-in fade-in slide-in-from-bottom-1 duration-200 bg-safety-refuse-bg">
      <div className="flex items-start gap-3 p-4">
        <ShieldAlert className="mt-0.5 size-6 shrink-0 text-confidence-insufficient" strokeWidth={1.5} />
        <div className="min-w-0 flex-1 space-y-2.5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <h3 className="text-[16px] font-semibold text-foreground">
              I can&apos;t answer this safely within scope.
            </h3>
            {(turn.confidence || typeof turn.confidenceScore === "number") && (
              <ConfidenceBadge
                level={turn.confidence ?? "insufficient"}
                score={turn.confidenceScore ?? 0}
                compact
              />
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="inline-block rounded-md border border-border bg-card px-2 py-0.5 font-mono text-[12px] text-confidence-insufficient">
              {turn.reason}
            </span>
            {turn.status && (
              <span className="inline-block rounded-md border border-border bg-card px-2 py-0.5 font-mono text-[12px] text-muted-foreground">
                {turn.status}
              </span>
            )}
          </div>
          <p className="whitespace-pre-wrap text-[14px] leading-relaxed text-muted-foreground">{turn.detail}</p>
          {turn.emergencyLine && (
            <p className="rounded-lg border border-confidence-low/30 bg-confidence-low/10 px-3 py-2 text-[15px] font-semibold text-foreground">
              {turn.emergencyLine}
            </p>
          )}
          {turn.nextAction && (
            <p className="text-[13px] text-foreground/80">
              Suggested next action: {turn.nextAction}
            </p>
          )}
        </div>
      </div>
      <p className="border-t border-border px-4 py-2.5 text-[12px] text-muted-foreground">
        This supports — not replaces — clinical judgment.
      </p>
    </Card>
  );
}
