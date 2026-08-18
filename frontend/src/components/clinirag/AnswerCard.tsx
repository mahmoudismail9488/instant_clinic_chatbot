import { AlertTriangle, ShieldAlert } from "lucide-react";
import { Card, CitationChip, ConfidenceBadge } from "./primitives";
import type { AnswerTurn, RefusalTurn } from "@/lib/clinirag-data";

export function UserMessage({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <p className="max-w-[80%] rounded-xl bg-secondary px-3.5 py-2 text-[15px] text-foreground">{text}</p>
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
    <Card className={turn.caution ? "border-t-2 border-t-safety-caution" : undefined}>
      {turn.caution && (
        <div className="flex items-start gap-2 rounded-t-xl bg-safety-caution-bg px-4 py-2.5 text-[13px] text-safety-caution">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" strokeWidth={1.5} />
          <span>{turn.caution}</span>
        </div>
      )}
      <div className="flex items-start justify-between gap-4 px-4 pt-4">
        <h3 className="font-mono text-[12px] uppercase tracking-wide text-muted-foreground">Recommendation</h3>
        <ConfidenceBadge level={turn.confidence} />
      </div>
      <p className="px-4 pt-2 text-[15px] leading-[1.6] text-foreground">
        <span className="font-semibold">{turn.recommendation.split(". ")[0]}.</span>{" "}
        {turn.recommendation.split(". ").slice(1).join(". ")}
      </p>

      <h3 className="px-4 pt-5 font-mono text-[12px] uppercase tracking-wide text-muted-foreground">
        Supporting evidence
      </h3>
      <ul className="space-y-2.5 px-4 pt-2">
        {turn.evidence.map((e) => (
          <li key={e.citation.chunkId} className="text-[15px] leading-[1.6] text-foreground">
            <span className="mr-2 text-muted-foreground">—</span>
            {e.text}
            <CitationChip
              citation={e.citation}
              onSelect={onCitation}
              active={activeChunk === e.citation.chunkId}
            />
          </li>
        ))}
      </ul>

      <p className="mt-5 rounded-b-xl border-t border-border px-4 py-2.5 text-[12px] text-muted-foreground">
        This supports — not replaces — clinical judgment.
      </p>
    </Card>
  );
}

export function RefusalCard({ turn }: { turn: RefusalTurn }) {
  return (
    <Card className="bg-safety-refuse-bg">
      <div className="flex items-start gap-3 p-4">
        <ShieldAlert className="mt-0.5 size-6 shrink-0 text-confidence-insufficient" strokeWidth={1.5} />
        <div className="space-y-2">
          <h3 className="text-[16px] font-semibold text-foreground">
            I can&apos;t answer this safely within scope.
          </h3>
          <span className="inline-block rounded-md border border-border bg-card px-2 py-0.5 font-mono text-[12px] text-confidence-insufficient">
            {turn.reason}
          </span>
          <p className="text-[14px] text-muted-foreground">{turn.detail}</p>
          {turn.emergencyLine && (
            <p className="text-[15px] font-semibold text-foreground">{turn.emergencyLine}</p>
          )}
        </div>
      </div>
      <p className="border-t border-border px-4 py-2.5 text-[12px] text-muted-foreground">
        This supports — not replaces — clinical judgment.
      </p>
    </Card>
  );
}