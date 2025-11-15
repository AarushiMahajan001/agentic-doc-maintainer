from typing import List, Dict
from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import INDEX_DIR, EMBEDDING_MODEL_NAME
from app.models import CodeChunk


class CodeSearchIndex:
    """
    Wrapper around a FAISS index + metadata for code chunks.
    """

    def __init__(self, index_dir: Path = INDEX_DIR):
        self.index_dir = index_dir
        self.index = None
        self.id_to_meta: Dict[int, Dict] = {}
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def _load_index_and_meta(self):
        index_path = self.index_dir / "code.index"
        meta_path = self.index_dir / "metadata.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                f"Did you run scripts/ingest_repo.py?"
            )
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found at {meta_path}. "
                f"Did you run scripts/ingest_repo.py?"
            )

        self.index = faiss.read_index(str(index_path))
        with open(meta_path, "r") as f:
            meta_list = json.load(f)

        # meta_list is a list of dicts; map by position
        self.id_to_meta = {i: m for i, m in enumerate(meta_list)}

    def ensure_loaded(self):
        if self.index is None or not self.id_to_meta:
            self._load_index_and_meta()

    def search(self, query: str, top_k: int = 5) -> List[CodeChunk]:
        """
        Search for the most relevant code chunks given a natural language query.
        """
        self.ensure_loaded()

        # Encode query to embedding
        emb = self.model.encode([query])
        emb = np.asarray(emb, dtype="float32")

        # Query FAISS index
        distances, indices = self.index.search(emb, top_k)

        results: List[CodeChunk] = []
        for idx in indices[0]:
            if int(idx) in self.id_to_meta:
                meta = self.id_to_meta[int(idx)]
                # Reconstruct the CodeChunk from stored metadata
                results.append(CodeChunk(**meta))

        return results


# Singleton-like helper for agents

_code_search_index: CodeSearchIndex | None = None


def _get_index() -> CodeSearchIndex:
    global _code_search_index
    if _code_search_index is None:
        _code_search_index = CodeSearchIndex()
    return _code_search_index


def search_code(query: str, top_k: int = 5) -> List[CodeChunk]:
    """
    Public helper used by agents.

    Example:
        chunks = search_code("trajectory estimation function", top_k=5)
    """
    index = _get_index()
    return index.search(query=query, top_k=top_k)
