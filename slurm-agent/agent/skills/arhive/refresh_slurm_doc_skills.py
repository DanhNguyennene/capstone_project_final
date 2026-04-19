#!/usr/bin/env python3
"""
Refresh local Slurm knowledge corpus from official SchedMD docs.

This script performs a real crawl of slurm.schedmd.com and writes markdown
pages under agent/skills/slurm_knowledge. It also writes a lightweight
slurm_doc_index.md skill file that points the agent to the corpus lookup tool.

Usage:
  python refresh_slurm_doc_skills.py
    python refresh_slurm_doc_skills.py --out-dir ./agent/skills/slurm_knowledge --max-pages 800
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from crawl_slurm_docs_to_mds import (
    DEFAULT_HOST,
    DEFAULT_START_URL,
    crawl_and_convert,
)


INDEX_NAME = "slurm_doc_index"
INDEX_TITLE = "Slurm Official Documentation Index"
INDEX_WHEN = "User asks documentation, syntax, or best-practice questions for Slurm commands."
INDEX_URL = "https://slurm.schedmd.com/documentation.html"


def _build_common_query_phrases() -> List[str]:
    return [
        "sbatch dependency afterok",
        "scancel array parent id",
        "scontrol hold release requeue",
        "job state codes pending running failed",
        "sacct format fields",
        "sinfo node state drained reason",
        "gres gpu syntax",
        "qos maxjobs maxcpus",
    ]


def _render_index_from_manifest(entries: List[Dict[str, str]], stamp: str, corpus_dir: Path) -> str:
    by_page = sorted(entries, key=lambda row: row.get("title", ""))[:40]
    host = "unknown"
    if by_page:
        first = by_page[0].get("url", "")
        parsed = urlparse(first)
        host = parsed.netloc or host

    lines = [
        f"# {INDEX_TITLE}",
        "",
        f"**When to use:** {INDEX_WHEN}",
        f"**Official source:** {INDEX_URL}",
        f"**Refreshed:** {stamp}",
        f"**Corpus directory:** {corpus_dir}",
        f"**Pages indexed:** {len(entries)}",
        "",
        "## Agent Routing",
        "- Use lookup_slurm_docs first for Slurm documentation questions.",
        "- Use concise topic queries to retrieve high-signal snippets quickly.",
        "- Fall back to web_search only when local corpus misses the topic.",
        "",
        "## Suggested Queries",
    ]

    for query in _build_common_query_phrases():
        lines.append(f"- lookup_slurm_docs(query=\"{query}\")")

    lines.extend(
        [
            "",
            "## Sample Pages",
        ]
    )

    for row in by_page[:20]:
        title = row.get("title", "Untitled")
        src = row.get("url", "")
        md_path = row.get("md_path", "")
        lines.append(f"- {title} ({src}) -> {md_path}")

    lines.extend(
        [
            "",
            "## Web Fallback",
            f"- If local corpus misses a topic, use: web_search(query=\"site:{host} <topic>\")",
        ]
    )

    return "\n".join(lines) + "\n"


def _load_manifest(corpus_dir: Path) -> List[Dict[str, str]]:
    manifest = corpus_dir / "manifest.json"
    if not manifest.exists():
        return []
    try:
        raw = manifest.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
    except Exception as exc:
        print(f"WARN: failed to read manifest {manifest}: {exc}", file=sys.stderr)
    return []


def refresh(
    out_dir: Path,
    timeout: int,
    start_url: str,
    host: str,
    max_pages: int,
    max_depth: int,
    delay: float,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    crawl_status = crawl_and_convert(
        start_url=start_url,
        host=host,
        out_dir=out_dir,
        timeout=timeout,
        max_pages=max_pages,
        max_depth=max_depth,
        delay_s=delay,
    )
    if crawl_status != 0:
        print("Doc crawl failed; keeping existing corpus if present.", file=sys.stderr)
        return crawl_status

    entries = _load_manifest(out_dir)
    index_content = _render_index_from_manifest(entries, stamp=stamp, corpus_dir=out_dir)
    index_target = Path(__file__).resolve().parent / f"{INDEX_NAME}.md"
    index_target.write_text(index_content, encoding="utf-8")
    print(f"Wrote {index_target}")

    print(f"Doc refresh complete: {len(entries)} pages crawled into {out_dir}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh Slurm docs corpus and markdown index skill")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent / "slurm_knowledge"),
        help="Directory to write crawled markdown corpus (default: agent/skills/slurm_knowledge)",
    )
    parser.add_argument(
        "--start-url",
        default=DEFAULT_START_URL,
        help="Seed URL to start crawling",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Allowed host for crawl",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="HTTP timeout seconds per page (default: 20)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1200,
        help="Maximum number of pages to convert (default: 1200)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="Maximum BFS depth from start URL (default: 8)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between requests in seconds (default: 0)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    return refresh(
        out_dir=out_dir,
        timeout=args.timeout,
        start_url=args.start_url,
        host=args.host,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
    )


if __name__ == "__main__":
    raise SystemExit(main())
