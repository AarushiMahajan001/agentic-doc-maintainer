"""
Walk data/repo, build code chunks + embeddings + FAISS index.

Usage:
    python scripts/ingest_repo.py
"""

import os
import sys
from pathlib import Path
import json
import ast

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# --- Make sure the project root is on sys.path ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import REPO_DIR, INDEX_DIR, EMBEDDING_MODEL_NAME
from app.models import CodeChunk


def extract_chunks_from_file(path: Path) -> list[CodeChunk]:
    """
    Very simple function-level chunking:
    - Each top-level function (ast.FunctionDef) becomes a CodeChunk.
    """
    try:
        src = path.read_text()
    except UnicodeDecodeError:
        print(f"[WARN] Could not read file (encoding issue): {path}")
        return []

    try:
        tree = ast.parse(src)
    except SyntaxError:
        print(f"[WARN] Could not parse file (syntax error): {path}")
        return []

    chunks: list[CodeChunk] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = node.body[-1].lineno if node.body else start
            code_lines = src.splitlines()[start - 1 : end]
            chunks.append(
                CodeChunk(
                    id=-1,  # will be filled later
                    file_path=str(path.relative_to(REPO_DIR)),
                    symbol_name=node.name,
                    start_line=start,
                    end_line=end,
                    code="\n".join(code_lines),
                )
            )
    return chunks


def main():
    print(f"[INFO] REPO_DIR = {REPO_DIR}")
    print(f"[INFO] INDEX_DIR = {INDEX_DIR}")

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    all_chunks: list[CodeChunk] = []

    py_files = list(REPO_DIR.rglob("*.py"))
    print(f"[INFO] Found {len(py_files)} Python files under {REPO_DIR}")

    for py_file in py_files:
        print(f"[INFO] Extracting chunks from {py_file}")
        all_chunks.extend(extract_chunks_from_file(py_file))

    if not all_chunks:
        print("[WARN] No code chunks found. Nothing to index.")
        return

    print(f"[INFO] Total extracted chunks: {len(all_chunks)}")

    texts = [c.code for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype="float32")

    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    index_path = INDEX_DIR / "code.index"
    meta_path = INDEX_DIR / "metadata.json"

    faiss.write_index(index, str(index_path))

    # Attach ids and write metadata
    meta_list = []
    for i, c in enumerate(all_chunks):
        c.id = i
        meta_list.append(c.dict())

    with meta_path.open("w") as f:
        json.dump(meta_list, f, indent=2)

    print(f"[INFO] Wrote FAISS index to {index_path}")
    print(f"[INFO] Wrote metadata for {len(meta_list)} chunks to {meta_path}")


if __name__ == "__main__":
    main()
