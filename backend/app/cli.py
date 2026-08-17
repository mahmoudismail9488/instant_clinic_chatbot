"""CLI entrypoint: ingest guidelines and query the RAG pipeline."""

from __future__ import annotations

import argparse
import sys
import textwrap
import traceback

from backend.app.config import get_settings
from backend.app.pipeline.chunking import infer_section_title
from backend.app.pipeline.evidence import format_evidence_header
from backend.app.pipeline.run import build_index, run_query


def _out(message: str = "") -> None:
    """Write user-facing CLI output.

    Some IDE terminals only reliably show stderr for this process, so we write
    interactive results there (progress already used stderr successfully).
    """
    try:
        print(message, file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stderr, "encoding", None) or "utf-8"
        sys.stderr.buffer.write((message + "\n").encode(encoding, errors="replace"))
        sys.stderr.buffer.flush()


def _print_query_result(result) -> None:
    _out("\n=== Query rewrite ===\n")
    _out(f"original : {result.original_query}")
    _out(f"rewritten: {result.rewritten_query}")

    if result.blocked:
        _out("\n=== Guardrails ===\n")
        reason = result.guardrail.reason if result.guardrail else "blocked"
        _out(f"BLOCKED — {reason}")
        _out("\n=== Answer ===\n")
        _out(result.answer)
        return

    _out("\n=== Answer ===\n")
    _out(result.answer or "(empty answer from model)")

    if result.conflict is not None:
        _out("\n=== Conflict detection ===\n")
        if result.conflict.has_conflict:
            _out(result.conflict.summary or "Conflict flagged")
            if result.conflict.sources:
                _out("sources: " + ", ".join(result.conflict.sources))
        else:
            _out("No material conflict detected across retrieved sources.")

    _out("\n=== Evidence / citations ===\n")
    if not result.citations:
        _out("(none)")
    else:
        for i, cite in enumerate(result.citations, start=1):
            excerpt = textwrap.shorten(cite.excerpt, width=280, placeholder=" …")
            title = infer_section_title(cite.excerpt, cite.section_title)
            header = format_evidence_header(
                score=cite.score,
                source=cite.source,
                chunk_index=cite.chunk_index,
                page=cite.page,
                section_number=cite.section_number,
                section_title=title,
            )
            _out(f"[{i}] {header}")
            _out(f"    {excerpt}")


def cmd_ingest(args: argparse.Namespace) -> int:
    settings = get_settings()
    _out(f"Ingesting from: {settings.raw_guidelines_dir}")
    if args.txt_only:
        _out("Mode: .txt files only")
    stats = build_index(txt_only=args.txt_only, rebuild=not args.append)
    _out(
        f"Done. documents={stats['documents']} chunks={stats['chunks']} "
        f"index_size={stats['index_size']}"
    )
    _out(f"Index path: {settings.vector_index_dir}")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    query = args.query.strip()
    if not query:
        _out("Query must be non-empty.")
        return 2
    _out("Running pipeline (rewrite → retrieve → generate → conflict check)…")
    result = run_query(query, top_k=args.top_k, progress=_out)
    _print_query_result(result)
    _out("Done.")
    return 0 if not result.blocked else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clinic",
        description="Instant Clinic CLI — ingest guidelines and ask grounded questions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Build/rebuild the vector index from data/raw_guidelines")
    ingest.add_argument(
        "--txt-only",
        action="store_true",
        help="Ingest only .txt guidelines (faster demo)",
    )
    ingest.add_argument(
        "--append",
        action="store_true",
        help="Append to existing index instead of rebuilding",
    )
    ingest.set_defaults(func=cmd_ingest)

    query = sub.add_parser("query", help="Ask a question and print answer + related chunks")
    query.add_argument("query", help="Natural-language clinical question")
    query.add_argument("--top-k", type=int, default=None, help="Number of chunks to retrieve")
    query.set_defaults(func=cmd_query)

    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        _out("Interrupted.")
        return 130
    except Exception as exc:
        _out(f"Error: {exc}")
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
