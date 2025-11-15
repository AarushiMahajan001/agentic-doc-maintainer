from typing import List
from app.models import DocTaskState, CodeChunk
from app.tools.code_search import search_code


def run_code_search_agent(state: DocTaskState) -> DocTaskState:
    """
    Use embedding-based search to pick relevant code chunks.
    """
    query = state.query or f"Key APIs related to module {state.module_path}"
    chunks: List[CodeChunk] = search_code(query, top_k=10)
    state.selected_chunks = chunks
    return state
