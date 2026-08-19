import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";
import { MetaRow, SourceLine } from "./primitives";
import type { EvidenceChunk } from "@/lib/clinirag-data";

function ChunkCard({
  chunk,
  active,
  maxScore,
}: {
  chunk: EvidenceChunk;
  active: boolean;
  maxScore: number;
}) {
  const [open, setOpen] = useState(false);
  const bar = maxScore > 0 ? Math.min(1, chunk.score / maxScore) : 0;

  return (
    <div
      id={`chunk-${chunk.id}`}
      className={cn(
        "rounded-xl border border-l-4 border-border bg-card p-3.5 transition-all duration-150",
        chunk.used ? "border-l-evidence" : "border-l-border opacity-90",
        active && "shadow-md ring-2 ring-evidence/40",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <SourceLine doc={chunk.doc} page={chunk.page} />
        <span
          className={cn(
            "shrink-0 rounded-md px-1.5 py-0.5 font-mono text-[11px]",
            chunk.used
              ? "bg-evidence/15 text-evidence"
              : "bg-muted text-muted-foreground",
          )}
        >
          {chunk.used ? "cited" : "unused"}
        </span>
      </div>
      <div className="mt-2.5 flex items-center gap-2">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className={cn("h-full rounded-full transition-all", chunk.used ? "bg-evidence" : "bg-muted-foreground/45")}
            style={{ width: `${bar * 100}%` }}
          />
        </div>
        <span className="w-10 text-right font-mono text-[12px] tabular-nums text-muted-foreground">
          {chunk.score.toFixed(2)}
        </span>
      </div>
      <p className={cn("mt-2.5 text-[14px] leading-[1.6] text-foreground", !open && "line-clamp-3")}>
        {chunk.excerpt}
      </p>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="mt-1.5 font-mono text-[12px] text-primary hover:text-primary-hover"
      >
        {open ? "Collapse" : "Show full chunk"}
      </button>
      <div className="mt-2 border-t border-border pt-2">
        <MetaRow chunkId={chunk.id} section={chunk.section} url={chunk.url} />
      </div>
    </div>
  );
}

export function EvidencePanel({
  chunks,
  activeChunk,
  judgeMode,
}: {
  chunks: EvidenceChunk[];
  activeChunk: string | null;
  judgeMode: boolean;
}) {
  const maxScore = useMemo(
    () => (chunks.length ? Math.max(...chunks.map((c) => c.score), 1e-6) : 1),
    [chunks],
  );
  const cited = chunks.filter((c) => c.used).length;

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-[14px] font-semibold text-foreground">Evidence</h2>
        <p className="mt-0.5 font-mono text-[12px] text-muted-foreground">
          Top-{chunks.length || 5} retrieved
          {chunks.length > 0 ? ` · ${cited} cited` : ""}
        </p>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {chunks.length === 0 ? (
          <p className="rounded-xl border border-dashed border-border p-4 text-[14px] leading-relaxed text-muted-foreground">
            No retrieval for this turn — the query was refused before search, or fell outside guideline scope.
          </p>
        ) : (
          chunks.map((c) => (
            <ChunkCard key={c.id} chunk={c} active={activeChunk === c.id} maxScore={maxScore} />
          ))
        )}
      </div>
      {judgeMode && chunks.length > 0 && (
        <div className="border-t border-border px-4 py-2.5 font-mono text-[12px] text-muted-foreground">
          Relative score bars · raw retrieval scores shown numerically
        </div>
      )}
    </div>
  );
}
