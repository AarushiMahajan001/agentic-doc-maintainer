from app.models import DocTaskState
from app.tools.doc_writer import generate_doc_for_chunk


def run_doc_writer_agent(state: DocTaskState) -> DocTaskState:
    """
    Generate Markdown docs for each selected chunk.
    """
    docs = {}
    for chunk in state.selected_chunks:
        docs[chunk.symbol_name] = generate_doc_for_chunk(chunk)
    state.draft_docs = docs
    return state
