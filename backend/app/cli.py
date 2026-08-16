"""CLI entrypoint: ingest guidelines and query the RAG pipeline."""

from __future__ import annotations

import argparse
import sys
import textwrap

from backend.app.config import get_settings
from backend.app.pipeline.run import build_index, run_query


def _print_query_result(result) -> None:
    print("\n=== Query rewrite ===\n")
    print(f"original : {result.original_query}")
    print(f"rewritten: {result.rewritten_query}")

    if result.blocked:
        print("\n=== Guardrails ===\n")
        reason = result.guardrail.reason if result.guardrail else "blocked"
        print(f"BLOCKED — {reason}")
        print("\n=== Answer ===\n")
        print(result.answer)
        return

    print("\n=== Answer ===\n")
    print(result.answer)

    if result.conflict is not None:
        print("\n=== Conflict detection ===\n")
        if result.conflict.has_conflict:
            print(result.conflict.summary or "Conflict flagged")
            if result.conflict.sources:
                print("sources:", ", ".join(result.conflict.sources))
        else:
            print("No material conflict detected across retrieved sources.")

    print("\n=== Evidence / citations ===\n")
    if not result.citations:
        print("(none)")
    else:
        for i, cite in enumerate(result.citations, start=1):
            excerpt = textwrap.shorten(cite.excerpt, width=280, placeholder=" …")
            print(f"[{i}] score={cite.score:.3f}  source={cite.source}  chunk={cite.chunk_index}")
            print(f"    {excerpt}")
            print()

    print("=== Related chunks ===\n")
    if not result.chunks:
        print("(none)")
        return
    for i, chunk in enumerate(result.chunks, start=1):
        excerpt = textwrap.shorten(chunk.text, width=360, placeholder=" …")
        print(f"[{i}] score={chunk.score:.3f}  source={chunk.source}  chunk={chunk.chunk_index}")
        print(excerpt)
        print()


def cmd_ingest(args: argparse.Namespace) -> int:
    settings = get_settings()
    print(f"Ingesting from: {settings.raw_guidelines_dir}")
    if args.txt_only:
        print("Mode: .txt files only")
    stats = build_index(txt_only=args.txt_only, rebuild=not args.append)
    print(
        f"Done. documents={stats['documents']} chunks={stats['chunks']} "
        f"index_size={stats['index_size']}"
    )
    print(f"Index path: {settings.vector_index_dir}")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    query = args.query.strip()
    if not query:
        print("Query must be non-empty.", file=sys.stderr)
        return 2
    result = run_query(query, top_k=args.top_k)
    _print_query_result(result)
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
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
