#!/usr/bin/env bash
# Update Slurm docs corpus + pre-compute semantic embeddings for RAG.
# Usage: ./update_slurm_docs.sh [--max-pages 300] [--delay 0.3]
set -euo pipefail
cd "$(dirname "$0")"

KNOWLEDGE_DIR="agent/skills/slurm_knowledge"
CRAWLER="agent/skills/arhive/crawl_slurm_docs_to_mds.py"
EMBEDDER="agent/skills/build_embeddings.py"

echo "=== Step 1: Crawl Slurm docs ==="
python "$CRAWLER" --out-dir "$KNOWLEDGE_DIR" "$@"

echo ""
echo "=== Step 2: Build semantic embeddings ==="
python "$EMBEDDER" --corpus-dir "$KNOWLEDGE_DIR"

echo ""
echo "=== Done! ==="
echo "Corpus: $KNOWLEDGE_DIR/"
echo "Embeddings: $KNOWLEDGE_DIR/embeddings.npz"
