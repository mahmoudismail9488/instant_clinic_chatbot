"""Step 3: re-index corpus per chunk config into isolated Qdrant collections, then retrieve."""

from __future__ import annotations

import argparse
from pathlib import Path

from backend.app.config import get_settings
from backend.app.pipeline.chunking import chunk_units
from backend.app.pipeline.embeddings import embed_texts
from backend.app.pipeline.ingestion import ingest_directory
from backend.app.services.llm_client import LLMClient
from eval.common import (
    CHUNK_CONFIGS,
    EVAL_CONFIG_KEYS,
    OUTPUT_DIR,
    format_section,
    load_questions,
    save_retrieval_csv,
    snippet,
)
from eval import qdrant_store


def build_collection(
    *,
    config_key: str,
    recreate: bool,
    txt_only: bool,
    client: LLMClient,
) -> dict[str, int]:
    cfg = CHUNK_CONFIGS[config_key]
    collection = cfg["collection"]
    settings = get_settings()
    qdrant = qdrant_store.get_client()

    existing = qdrant_store.list_collections(qdrant)
    if collection in existing and not recreate:
        print(
            f"Collection '{collection}' already exists — skipping index (use --recreate to overwrite)."
        )
        return {"documents": -1, "chunks": -1, "skipped": 1}

    # New collection path: create after we know vector dim (or recreate)
    docs = ingest_directory(settings.raw_guidelines_dir, txt_only=txt_only)
    all_ids: list[str] = []
    all_texts: list[str] = []
    all_payloads: list[dict] = []

    for doc in docs:
        chunks = chunk_units(
            doc.units,
            source=doc.source,
            source_path=str(doc.source_path),
            chunk_size=cfg["chunk_size"],
            overlap=cfg["overlap"],
        )
        print(f"  [{config_key}] {doc.source}: {len(chunks)} chunks")
        for ch in chunks:
            cid = f"{ch.source}::{ch.index}"
            all_ids.append(cid)
            all_texts.append(ch.text)
            all_payloads.append(
                {
                    "chunk_id": cid,
                    "text": ch.text,
                    "document": ch.source,
                    "source": ch.source,
                    "source_path": ch.source_path,
                    "chunk_index": ch.index,
                    "page": ch.page,
                    "section_number": ch.section_number,
                    "section_title": ch.section_title,
                    "section": format_section(ch.section_number, ch.section_title),
                    "config": config_key,
                }
            )

    if not all_texts:
        raise RuntimeError("No chunks produced for indexing")

    print(f"Embedding {len(all_texts)} chunks for {collection}…")
    vectors: list[list[float]] = []
    batch = 64
    for start in range(0, len(all_texts), batch):
        part = all_texts[start : start + batch]
        vectors.extend(embed_texts(part, client=client))
        print(f"  embedded {min(start + batch, len(all_texts))}/{len(all_texts)}")

    dim = len(vectors[0])
    qdrant_store.ensure_collection(qdrant, collection, vector_size=dim, recreate=recreate or collection not in existing)
    # upsert in batches with global numeric ids
    for start in range(0, len(all_ids), 256):
        qdrant_store.upsert_chunks(
            qdrant,
            collection,
            ids=all_ids[start : start + 256],
            vectors=vectors[start : start + 256],
            payloads=all_payloads[start : start + 256],
            id_offset=start,
        )
    return {"documents": len(docs), "chunks": len(all_ids), "skipped": 0}


def retrieve_config(
    *,
    config_key: str,
    top_k: int,
    client: LLMClient,
) -> Path:
    cfg = CHUNK_CONFIGS[config_key]
    collection = cfg["collection"]
    qdrant = qdrant_store.get_client()
    if collection not in qdrant_store.list_collections(qdrant):
        raise SystemExit(f"Missing collection {collection}. Run indexing first.")

    questions = load_questions()
    rows = []
    for q in questions:
        emb = client.embed([q["question"]])[0]
        hits = qdrant_store.search(qdrant, collection, emb, top_k=top_k)
        for rank, hit in enumerate(hits, start=1):
            rows.append(
                {
                    "question_id": q["question_id"],
                    "question": q["question"],
                    "config": config_key,
                    "rank": rank,
                    "chunk_id": hit["chunk_id"],
                    "score": hit["score"],
                    "document": hit["document"],
                    "page": hit["page"] if hit["page"] is not None else "",
                    "section_number": hit.get("section_number", ""),
                    "section_title": hit.get("section_title", ""),
                    "section": hit.get("section")
                    or format_section(hit.get("section_number"), hit.get("section_title")),
                    "chunk_text_snippet": hit["chunk_text_snippet"] or snippet(hit["text"]),
                    "chunk_text": hit["text"],
                }
            )
    out = OUTPUT_DIR / f"retrieval_results_{config_key}.csv"
    save_retrieval_csv(rows, out)
    print(f"Wrote {len(rows)} rows → {out}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-index + retrieve per chunk config (Qdrant)")
    parser.add_argument(
        "--config",
        choices=[*EVAL_CONFIG_KEYS, "all"],
        default="all",
    )
    parser.add_argument("--index-only", action="store_true")
    parser.add_argument("--retrieve-only", action="store_true")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate collection")
    parser.add_argument("--yes", action="store_true", help="Confirm --recreate without prompt")
    parser.add_argument("--txt-only", action="store_true")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    if args.recreate and not args.yes:
        answer = input(
            "This will DELETE and recreate the selected Qdrant collection(s). Type 'yes' to continue: "
        )
        if answer.strip().lower() != "yes":
            print("Aborted.")
            return 1

    keys = list(EVAL_CONFIG_KEYS) if args.config == "all" else [args.config]
    client = LLMClient()

    if not args.retrieve_only:
        for key in keys:
            print(f"\n=== Indexing {key} → {CHUNK_CONFIGS[key]['collection']} ===")
            stats = build_collection(
                config_key=key,
                recreate=args.recreate,
                txt_only=args.txt_only,
                client=client,
            )
            print(stats)

    if not args.index_only:
        for key in keys:
            print(f"\n=== Retrieving {key} ===")
            retrieve_config(config_key=key, top_k=args.top_k, client=client)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
