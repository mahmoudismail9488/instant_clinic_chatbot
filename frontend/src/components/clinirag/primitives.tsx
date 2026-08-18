import { FileText, Hash, Link2, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Citation, Confidence } from "@/lib/clinirag-data";

const confidenceMap: Record<Confidence, { label: string; color: string; hint: string }> = {
  high: {
    label: "High",
    color: "text-confidence-high border-confidence-high/30 bg-confidence-high/8",
    hint: "Mean retrieval similarity 0.85 · 3/3 claims cited",
  },
  medium: {
    label: "Medium",
    color: "text-confidence-medium border-confidence-medium/30 bg-confidence-medium/8",
    hint: "Mean retrieval similarity 0.74 · 2/2 claims cited",
  },
  low: {
    label: "Low",
    color: "text-confidence-low border-confidence-low/30 bg-confidence-low/8",
    hint: "Mean retrieval similarity below 0.60",
  },
  insufficient: {
    label: "Insufficient Evidence",
    color: "text-confidence-insufficient border-confidence-insufficient/30 bg-confidence-insufficient/8",
    hint: "No chunk cleared the grounding threshold — refusal is the correct output",
  },
};

export function ConfidenceBadge({ level }: { level: Confidence }) {
  const c = confidenceMap[level];
  return (
    <span
      title={c.hint}
      className={cn(
        "inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[12px] leading-5",
        c.color,
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {c.label}
    </span>
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
      {citation.doc} · {citation.page ? `p.${citation.page}` : "p.n/a"} · {citation.section}
    </button>
  );
}

export function SourceLine({ doc, page }: { doc: string; page: number }) {
  return (
    <div className="flex items-center gap-1.5 text-[14px] font-semibold text-foreground">
      <FileText className="size-4 text-muted-foreground" strokeWidth={1.5} />
      {doc}
      <span className="font-mono text-[12px] font-normal text-muted-foreground">p.{page}</span>
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
      <span>·</span>
      <span className="truncate">{url}</span>
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