from __future__ import annotations

import argparse
from pathlib import Path

import chromadb


def build_source_client(source_path: str):
    return chromadb.PersistentClient(path=source_path)


def build_target_client():
    return chromadb.CloudClient()


def copy_collection(source_collection, target_collection) -> int:
    payload = source_collection.get(include=["embeddings", "documents", "metadatas"])
    ids = payload.get("ids", [])
    if not ids:
        return 0

    target_collection.upsert(
        ids=ids,
        embeddings=payload.get("embeddings"),
        documents=payload.get("documents"),
        metadatas=payload.get("metadatas"),
    )
    return len(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy local Chroma collections to Chroma Cloud.")
    parser.add_argument("--source-path", required=True, help="Path to the local persistent Chroma database")
    args = parser.parse_args()

    source_path = Path(args.source_path)
    if not source_path.exists():
        raise SystemExit(f"Source path does not exist: {source_path}")

    source_client = build_source_client(str(source_path))
    target_client = build_target_client()

    total_copied = 0
    for collection in source_client.list_collections():
        source_collection = source_client.get_collection(name=collection.name)
        target_collection = target_client.get_or_create_collection(name=collection.name)
        total_copied += copy_collection(source_collection, target_collection)

    print(f"Copied {total_copied} records from {source_path} to Chroma Cloud")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
