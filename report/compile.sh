#!/bin/bash
# Compile LaTeX document with bibliography support

cd "$(dirname "$0")"

echo "=== Compiling main.tex ==="

# First pass
echo "[1/4] Running xelatex (first pass)..."
xelatex -interaction=nonstopmode main.tex > /dev/null 2>&1

# Run biber for bibliography
echo "[2/4] Running biber..."
biber main > /dev/null 2>&1

# Second pass (resolve references)
echo "[3/4] Running xelatex (second pass)..."
xelatex -interaction=nonstopmode main.tex > /dev/null 2>&1

# Third pass (finalize)
echo "[4/4] Running xelatex (final pass)..."
xelatex -interaction=nonstopmode main.tex > /dev/null 2>&1

# echo "transfer to remote laptop (overwriting existing file)..."
# scp main.pdf danhbuonba@10.0.0.2:'/mnt/c/Users/Danh Nguyen/Downloads/main.pdf'
# Check result
if [ -f main.pdf ]; then
    echo "=== Done! Output: main.pdf ==="
else
    echo "=== Compilation failed. Check main.log for errors ==="
    exit 1
fi
