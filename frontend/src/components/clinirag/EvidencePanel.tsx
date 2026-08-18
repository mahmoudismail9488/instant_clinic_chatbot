import { useState } from "react";
import { cn } from "@/lib/utils";
import { MetaRow, SourceLine } from "./primitives";
import type { EvidenceChunk } from "@/lib/clinirag-data";

function ChunkCard({ chunk, active }: { chunk: EvidenceChunk; active: boolean }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      id={`chunk-${chunk.id}`}
      className={cn(
        "rounded-xl border border-l-4 border-border bg-card p-3.5 transition-shadow duration-150",
        chunk.used ? "border-l-evidence" : "border-l-border",
        active && "shadow-sm ring-2 ring-evidence/40",
      )}
    >
      <SourceLine doc={chunk.doc} page={chunk.page} />
      <div className="mt-2 flex items-center gap-2">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className={cn("h-full rounded-full", chunk.used ? "bg-evidence" : "bg-muted-foreground/50")}
            style={{ width: `${chunk.score * 100}%` }}
          />
        </div>
        <span className="font-mono text-[12px] text-muted-foreground">{chunk.score.toFixed(2)}</span>
      </div>
      <p className={cn("mt-2 text-[14px] leading-[1.6] text-foreground", !open && "line-clamp-3")}>
        {chunk.excerpt}
      </p>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="mt-1 font-mono text-[12px] text-primary hover:text-primary-hover"
      >
        {open ? "collapse chunk" : "show full chunk"}
      </button>
      <div className="mt-2 border-t border-border pt-2">
        <MetaRow chunkId={chunk.id} section={chunk.section} url={chunk.url} />
      </div>
      <p className="mt-2 font-mono text-[12px] text-muted-foreground">
        {chunk.used ? "cited in answer" : "retrieved · not cited"}
      </p>
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
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-[14px] font-semibold text-foreground">
          Evidence used for this answer{" "}
          <span className="font-mono text-[12px] font-normal text-muted-foreground">(Top-K = 5)</span>
        </h2>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {chunks.length === 0 ? (
          <p className="rounded-xl border border-dashed border-border p-4 text-[14px] text-muted-foreground">
            No retrieval performed — query fell outside guideline scope.
          </p>
        ) : (
          chunks.map((c) => <ChunkCard key={c.id} chunk={c} active={activeChunk === c.id} />)
        )}
      </div>
      {judgeMode && chunks.length > 0 && (
        <div className="border-t border-border px-4 py-2.5 font-mono text-[12px] text-muted-foreground">
          Precision@5 for this query: <span className="text-confidence-high">0.80</span>
        </div>
      )}
    </div>
  );
}