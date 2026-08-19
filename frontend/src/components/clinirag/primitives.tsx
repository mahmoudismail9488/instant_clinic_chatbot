import { FileText, Hash, Link2, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Citation, Confidence } from "@/lib/clinirag-data";

const confidenceMap: Record<
  Confidence,
  { short: string; label: string; color: string; bar: string; hint: string }
> = {
  high: {
    short: "High",
    label: "High",
    color: "text-confidence-high border-confidence-high/30 bg-confidence-high/8",
    bar: "bg-confidence-high",
    hint: "Strong retrieval + full citation coverage",
  },
  medium: {
    short: "Med",
    label: "Medium",
    color: "text-confidence-medium border-confidence-medium/30 bg-confidence-medium/8",
    bar: "bg-confidence-medium",
    hint: "Adequate evidence; review citations carefully",
  },
  low: {
    short: "Low",
    label: "Low",
    color: "text-confidence-low border-confidence-low/30 bg-confidence-low/8",
    bar: "bg-confidence-low",
    hint: "Weak or partial evidence support",
  },
  insufficient: {
    short: "—",
    label: "Insufficient",
    color:
      "text-confidence-insufficient border-confidence-insufficient/30 bg-confidence-insufficient/8",
    bar: "bg-confidence-insufficient",
    hint: "No answerable evidence — refusal is correct",
  },
};

/** Fallback score when API omits confidence_score. */
export function scoreForLevel(level: Confidence): number {
  switch (level) {
    case "high":
      return 0.88;
    case "medium":
      return 0.68;
    case "low":
      return 0.42;
    default:
      return 0;
  }
}

export function ConfidenceBadge({
  level,
  score,
  compact = false,
}: {
  level: Confidence;
  score?: number | null;
  compact?: boolean;
}) {
  const c = confidenceMap[level];
  const value = typeof score === "number" && Number.isFinite(score) ? score : scoreForLevel(level);
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);

  return (
    <div
      title={`${c.hint} · Evidence score ${value.toFixed(2)} (not a clinical probability)`}
      className={cn(
        "inline-flex shrink-0 flex-col gap-1 rounded-lg border px-2.5 py-1.5",
        c.color,
        compact && "py-1",
      )}
    >
      <div className="flex items-center gap-2 font-mono text-[12px] leading-none">
        <span className="size-1.5 shrink-0 rounded-full bg-current" />
        <span className="tabular-nums font-semibold">{value.toFixed(2)}</span>
        <span className="text-current/70">·</span>
        <span>{c.short}</span>
      </div>
      {!compact && (
        <div className="h-1 w-[7.5rem] overflow-hidden rounded-full bg-current/15">
          <div className={cn("h-full rounded-full transition-all duration-300", c.bar)} style={{ width: `${pct}%` }} />
        </div>
      )}
    </div>
  );
}

export function CitationChip({
  citation,
  onSelect,
  active,
}: {
  citation: Citation;
  onSelect?: (chunkId: string) => void;
  active?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(citation.chunkId)}
      className={cn(
        "ml-1 inline-flex items-center gap-1 rounded-md border border-evidence/35 bg-evidence-soft px-1.5 py-0.5 font-mono text-[12px] text-evidence transition-colors duration-150 hover:border-evidence hover:bg-evidence/12",
        active && "ring-2 ring-evidence/40",
      )}
    >
      <Link2 className="size-3" strokeWidth={1.5} />
      {citation.doc} · p.{citation.page} · {citation.section}
    </button>
  );
}

export function SourceLine({ doc, page }: { doc: string; page: number }) {
  return (
    <div className="flex items-center gap-1.5 text-[14px] font-semibold text-foreground">
      <FileText className="size-4 text-muted-foreground" strokeWidth={1.5} />
      <span className="truncate">{doc}</span>
      <span className="shrink-0 font-mono text-[12px] font-normal text-muted-foreground">p.{page}</span>
    </div>
  );
}

export function MetaRow({ chunkId, section, url }: { chunkId: string; section: string; url: string }) {
  return (
    <div className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[12px] text-muted-foreground">
      <span className="inline-flex items-center gap-1">
        <Hash className="size-3" strokeWidth={1.5} />
        {chunkId}
      </span>
      <span>·</span>
      <span>{section}</span>
      {url ? (
        <>
          <span>·</span>
          <span className="truncate">{url}</span>
        </>
      ) : null}
    </div>
  );
}

export function GuardrailIndicator() {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-confidence-high/30 bg-confidence-high/8 px-2 py-1 font-mono text-[12px] text-confidence-high">
      <ShieldCheck className="size-3.5" strokeWidth={1.5} />
      Guardrail: Active
    </span>
  );
}

export function Card({
  className,
  children,
}: {
  className?: string | undefined;
  children: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card transition-shadow duration-150 hover:shadow-sm",
        className,
      )}
    >
      {children}
    </div>
  );
}
