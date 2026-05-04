#!/usr/bin/env python3
"""
Pre-compute sentence-transformer embeddings for the Slurm docs corpus.

Saves a compressed .npz file that the agent loads at startup instead of
re-embedding every time. This makes agent startup ~2s faster.

Usage:
    python build_embeddings.py
    python build_embeddings.py --corpus-dir ./agent/skills/slurm_knowledge
    python build_embeddings.py --model sentence-transformers/all-MiniLM-L6-v2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np


def _clean_content(content: str) -> str:
    if content.startswith("---"):
        end = content.find("---", 3)
        if end >= 0:
            return content[end + 3:].strip()
    return content.strip()


def _title_for(content: str, fallback: str) -> str:
    m = re.search(r'^title:\s*"?([^"\n]+)"?', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def _chunk_doc(content: str) -> list[str]:
    """Split a document into chunks (same logic as tools.py)."""
    body = _clean_content(content)
    parts = re.split(r"\n(?=#{1,3}\s+)", body)
    chunks = []
    for part in parts:
        compact = re.sub(r"\n{3,}", "\n\n", part).strip()
        if len(compact) < 80:
            continue
        if len(compact) <= 1400:
            chunks.append(compact)
            continue
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", compact) if p.strip()]
        buffer = ""
        for paragraph in paragraphs:
            candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            if len(candidate) > 1400 and buffer:
                chunks.append(buffer)
                buffer = paragraph
            else:
                buffer = candidate
        if buffer:
            chunks.append(buffer[:1800])
    return chunks


def build_embeddings(corpus_dir: Path, model_name: str) -> Path:
    from sentence_transformers import SentenceTransformer

    # Load all docs
    docs: dict[str, str] = {}
    for f in sorted(corpus_dir.rglob("*.md")):
        if f.name in ("SLURM_DOCS_INDEX.md", "manifest.json"):
            continue
        content = f.read_text(encoding="utf-8").strip()
        if content:
            rel = f.relative_to(corpus_dir).as_posix()
            docs[rel] = content

    print(f"Loaded {len(docs)} docs from {corpus_dir}")

    # Build chunks (same order as tools.py)
    chunk_metadata = []  # list of {path, title, chunk_text}
    for doc_path, content in sorted(docs.items()):
        title = _title_for(content, doc_path)
        for chunk in _chunk_doc(content):
            chunk_metadata.append({
                "path": doc_path,
                "title": title,
                "text": f"{title}: {chunk[:512]}",
            })

    print(f"Total chunks: {len(chunk_metadata)}")

    # Load model and embed
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name, device="cuda")

    print("Encoding chunks...")
    t0 = time.time()
    embeddings = model.encode(
        [c["text"] for c in chunk_metadata],
        batch_size=256,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    elapsed = time.time() - t0
    print(f"Embedded {len(chunk_metadata)} chunks in {elapsed:.1f}s — shape: {embeddings.shape}")

    # Save
    out_path = corpus_dir / "embeddings.npz"
    np.savez_compressed(
        out_path,
        embeddings=embeddings,
        # Store metadata as JSON string for portability
        metadata=json.dumps(chunk_metadata, ensure_ascii=False),
    )
    print(f"Saved: {out_path} ({out_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build semantic embeddings for Slurm docs corpus")
    parser.add_argument(
        "--corpus-dir",
        default=str(Path(__file__).resolve().parent / "slurm_knowledge"),
        help="Path to the slurm_knowledge directory",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence-transformer model name",
    )
    args = parser.parse_args()
    build_embeddings(Path(args.corpus_dir).resolve(), args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
