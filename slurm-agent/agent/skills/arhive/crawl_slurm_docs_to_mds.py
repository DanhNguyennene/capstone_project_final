#!/usr/bin/env python3
"""
Crawl Slurm official documentation and convert pages into local Markdown corpus.

This script is intended for agent pre-run knowledge sync:
- Crawls slurm.schedmd.com HTML docs from a seed page
- Converts each page to a Markdown file
- Builds a manifest JSON + markdown index for efficient local lookup

Usage examples:
  python crawl_slurm_docs_to_mds.py
  python crawl_slurm_docs_to_mds.py --max-pages 300 --max-depth 6
    python crawl_slurm_docs_to_mds.py --out-dir ./agent/skills/slurm_knowledge
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.request import Request, urlopen

DEFAULT_START_URL = "https://slurm.schedmd.com/documentation.html"
DEFAULT_HOST = "slurm.schedmd.com"

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".gz", ".tar", ".tgz", ".bz2", ".xz",
    ".mp4", ".mp3", ".wav",
    ".css", ".js", ".map",
    ".woff", ".woff2", ".ttf", ".eot",
}

SKIP_PATH_FRAGMENTS = {
    "/archive/",
    "/bugs/",
    "/ticket",
}


def _fetch_html(url: str, timeout: int) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "slurm-doc-crawler/1.0 (+https://slurm.schedmd.com)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        ctype = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ctype:
            raise ValueError(f"non-html content type: {ctype}")
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def _normalize_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    try:
        clean, _frag = urldefrag(raw_url.strip())
        parsed = urlparse(clean)
    except ValueError:
        return ""
    if parsed.scheme not in {"http", "https"}:
        return ""
    path = parsed.path or "/"
    norm = parsed._replace(path=re.sub(r"//+", "/", path), query="", fragment="")
    try:
        return norm.geturl()
    except ValueError:
        return ""


def _is_allowed_doc_url(url: str, host: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.netloc != host:
        return False

    path = (parsed.path or "/").lower()
    for frag in SKIP_PATH_FRAGMENTS:
        if frag in path:
            return False

    suffix = Path(path).suffix.lower()
    if suffix in SKIP_EXTENSIONS:
        return False

    # Keep only likely doc pages.
    if suffix and suffix != ".html":
        return False

    # Allow .html pages, directory-like paths, and extensionless command pages.
    return True


def _extract_links(page_html: str, base_url: str, host: str) -> List[str]:
    links: Set[str] = set()
    for match in re.finditer(r"href\s*=\s*(['\"])(.*?)\1", page_html, flags=re.IGNORECASE | re.DOTALL):
        href = html.unescape(match.group(2)).strip()
        if not href:
            continue
        if href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        try:
            joined = urljoin(base_url, href)
        except ValueError:
            continue
        full = _normalize_url(joined)
        if _is_allowed_doc_url(full, host):
            links.add(full)

    return sorted(links)


def _strip_tags(text: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_title(page_html: str) -> str:
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", page_html)
    if not m:
        return "Slurm Documentation"
    title = _strip_tags(m.group(1))
    return title or "Slurm Documentation"


def _extract_main_html(page_html: str) -> str:
    def _extract_balanced_div(html_text: str, pattern: str) -> str:
        m = re.search(pattern, html_text)
        if not m:
            return ""
        start = m.end()
        depth = 1
        token_re = re.compile(r"(?is)<div\b[^>]*>|</div\s*>")
        for tok in token_re.finditer(html_text, start):
            txt = tok.group(0).lower()
            if txt.startswith("</div"):
                depth -= 1
                if depth == 0:
                    return html_text[start:tok.start()]
            else:
                depth += 1
        return ""

    # Prefer semantic containers if present.
    for pattern in [
        r"(?is)<main[^>]*>(.*?)</main>",
        r"(?is)<article[^>]*>(.*?)</article>",
    ]:
        m = re.search(pattern, page_html)
        if m:
            return m.group(1)

    # Slurm docs commonly use nested div-based content blocks.
    for pattern in [
        r"(?is)<div[^>]+id=['\"]content['\"][^>]*>",
        r"(?is)<div[^>]+class=['\"][^'\"]*content[^'\"]*['\"][^>]*>",
    ]:
        block = _extract_balanced_div(page_html, pattern)
        if block:
            return block

    # Final fallback: whole body.
    m = re.search(r"(?is)<body[^>]*>(.*?)</body>", page_html)
    if m:
        return m.group(1)
    return page_html


def _convert_links_to_md(text: str, base_url: str) -> str:
    def repl(match: re.Match) -> str:
        href = html.unescape(match.group(2)).strip()
        label_html = match.group(3)
        label = _strip_tags(label_html)
        if not label:
            label = href
        try:
            absolute = _normalize_url(urljoin(base_url, href)) or href
        except ValueError:
            absolute = href
        return f"[{label}]({absolute})"

    return re.sub(
        r"(?is)<a\s+[^>]*href\s*=\s*(['\"])(.*?)\1[^>]*>(.*?)</a>",
        repl,
        text,
    )


def _html_to_markdown(page_html: str, base_url: str, title: str) -> str:
    body = _extract_main_html(page_html)

    # Remove known noisy containers.
    body = re.sub(r"(?is)<nav[^>]*>.*?</nav>", " ", body)
    body = re.sub(r"(?is)<footer[^>]*>.*?</footer>", " ", body)
    body = re.sub(r"(?is)<aside[^>]*>.*?</aside>", " ", body)

    body = _convert_links_to_md(body, base_url)

    # Code blocks first.
    body = re.sub(
        r"(?is)<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        lambda m: "\n```text\n" + html.unescape(m.group(1)).strip() + "\n```\n",
        body,
    )
    body = re.sub(
        r"(?is)<pre[^>]*>(.*?)</pre>",
        lambda m: "\n```text\n" + _strip_tags(m.group(1)).strip() + "\n```\n",
        body,
    )

    # Headings.
    for i in range(6, 0, -1):
        body = re.sub(
            rf"(?is)<h{i}[^>]*>(.*?)</h{i}>",
            lambda m, level=i: f"\n{'#' * level} {_strip_tags(m.group(1))}\n",
            body,
        )

    # Lists and paragraphs.
    body = re.sub(r"(?is)<li[^>]*>(.*?)</li>", lambda m: "\n- " + _strip_tags(m.group(1)), body)
    body = re.sub(r"(?is)</(ul|ol)>", "\n", body)
    body = re.sub(r"(?is)<(ul|ol)[^>]*>", "\n", body)
    body = re.sub(r"(?is)<br\s*/?>", "\n", body)
    body = re.sub(r"(?is)</(p|div|section|article|table|tr|td|th)>", "\n", body)
    body = re.sub(r"(?is)<(p|div|section|article|table|tr|td|th)[^>]*>", "\n", body)

    # Inline code.
    body = re.sub(r"(?is)<code[^>]*>(.*?)</code>", lambda m: "`" + _strip_tags(m.group(1)) + "`", body)

    # Remove all remaining tags and normalize whitespace.
    body = re.sub(r"(?is)<[^>]+>", " ", body)
    body = html.unescape(body)

    lines: List[str] = []
    for raw in body.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        if line.lower() in {"home", "next", "previous", "up"}:
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Guarantee top title.
    if not text.startswith("# "):
        text = f"# {title}\n\n" + text

    return text + "\n"


def _url_to_output_path(url: str, out_dir: Path) -> Tuple[Path, str]:
    parsed = urlparse(url)
    rel = (parsed.path or "/").lstrip("/")

    if not rel:
        rel = "index.html"
    elif rel.endswith("/"):
        rel = rel + "index.html"
    elif "." not in Path(rel).name:
        rel = rel + ".html"

    rel_path = Path(rel).with_suffix(".md")
    target = out_dir / rel_path
    return target, rel_path.as_posix()


def _is_directory_index_page(url: str, title: str) -> bool:
    t = (title or "").strip().lower()
    u = (url or "").strip().lower()
    if t.startswith("index of /"):
        return True
    if u.endswith("/index.html") and "slurm.schedmd.com/archive/" in u:
        return True
    return False


def _build_markdown_index(entries: List[Dict[str, str]]) -> str:
    lines = [
        "# Slurm Docs Local Corpus Index",
        "",
        "This file is generated by crawl_slurm_docs_to_mds.py.",
        "",
        "## Usage",
        "- Query by command name (sbatch, scancel, scontrol, squeue, ...)",
        "- Query by topic (job states, dependencies, arrays, reservations, accounting)",
        "",
        f"## Total Pages: {len(entries)}",
        "",
        "## Pages",
    ]

    for item in sorted(entries, key=lambda x: x.get("md_path", "")):
        title = item.get("title", "Untitled")
        md_path = item.get("md_path", "")
        src = item.get("url", "")
        lines.append(f"- [{title}]({md_path})")
        lines.append(f"  - Source: {src}")

    return "\n".join(lines) + "\n"


def crawl_and_convert(
    start_url: str,
    host: str,
    out_dir: Path,
    timeout: int,
    max_pages: int,
    max_depth: int,
    delay_s: float,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    visited: Set[str] = set()
    queued: Set[str] = set()
    queue: Deque[Tuple[str, int]] = deque()
    entries: List[Dict[str, str]] = []

    start = _normalize_url(start_url)
    if not _is_allowed_doc_url(start, host):
        print(f"ERROR: start URL is not an allowed docs URL: {start_url}", file=sys.stderr)
        return 2

    queue.append((start, 0))
    queued.add(start)

    while queue and len(entries) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        if depth > max_depth:
            continue

        try:
            page_html = _fetch_html(url, timeout=timeout)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            print(f"WARN: skip {url} ({exc})", file=sys.stderr)
            continue
        except Exception as exc:
            print(f"WARN: unexpected fetch error {url} ({exc})", file=sys.stderr)
            continue

        title = _extract_title(page_html)
        if _is_directory_index_page(url, title):
            print(f"Skip index-like page: {url}")
            continue

        markdown = _html_to_markdown(page_html, base_url=url, title=title)

        target_path, rel_md = _url_to_output_path(url, out_dir)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        stamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        sanitized_title = title.replace('"', "'")
        frontmatter = (
            "---\n"
            f"source_url: {url}\n"
            f"source_host: {host}\n"
            f"fetched_at_utc: {stamp}\n"
            f"title: \"{sanitized_title}\"\n"
            "---\n\n"
        )
        target_path.write_text(frontmatter + markdown, encoding="utf-8")

        excerpt = re.sub(r"\s+", " ", markdown).strip()[:280]
        entries.append(
            {
                "url": url,
                "title": title,
                "md_path": rel_md,
                "depth": depth,
                "word_count": str(len(markdown.split())),
                "excerpt": excerpt,
            }
        )

        print(f"Saved [{len(entries)}] {rel_md} <- {url}")

        # Discover links for BFS crawl.
        if depth < max_depth:
            links = _extract_links(page_html, base_url=url, host=host)
            for link in links:
                if link in visited or link in queued:
                    continue
                queue.append((link, depth + 1))
                queued.add(link)

        if delay_s > 0:
            time.sleep(delay_s)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    index_path = out_dir / "SLURM_DOCS_INDEX.md"
    index_path.write_text(_build_markdown_index(entries), encoding="utf-8")

    print(f"Wrote manifest: {manifest_path}")
    print(f"Wrote index:    {index_path}")
    print(f"Done. Pages converted: {len(entries)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Crawl Slurm docs and convert to markdown corpus")
    parser.add_argument("--start-url", default=DEFAULT_START_URL, help="Seed URL to start crawling")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Allowed host for crawl")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent / "slurm_knowledge"),
        help="Output directory for markdown corpus",
    )
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument("--max-pages", type=int, default=1200, help="Maximum number of pages to convert")
    parser.add_argument("--max-depth", type=int, default=8, help="Maximum BFS depth from start URL")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests in seconds")

    args = parser.parse_args()
    out_dir = Path(args.out_dir).resolve()

    return crawl_and_convert(
        start_url=args.start_url,
        host=args.host,
        out_dir=out_dir,
        timeout=args.timeout,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay_s=args.delay,
    )


if __name__ == "__main__":
    raise SystemExit(main())
