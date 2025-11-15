from app.models import DocTaskState
from app.agents.planner_agent import plan_doc_task
from app.agents.code_search_agent import run_code_search_agent
from app.agents.doc_writer_agent import run_doc_writer_agent
from app.agents.evaluator_agent import run_evaluator_agent
from app.tools.doc_writer import generate_module_overview
from app.tools.file_ops import write_doc_markdown


def run_documentation_pipeline(module_path: str, query: str | None = None) -> DocTaskState:
    """
    End-to-end pipeline:
    - plan
    - search for relevant code chunks
    - generate docs
    - evaluate docs
    - assemble final markdown
    - write markdown to disk in data/docs/
    """
    state = DocTaskState(module_path=module_path, query=query)

    # 1. Planning (currently trivial)
    state = plan_doc_task(state)

    # 2. Code search (FAISS + embeddings)
    state = run_code_search_agent(state)

    # 3. Doc writing (Groq)
    state = run_doc_writer_agent(state)

    # 4. Evaluation (Groq judge)
    state = run_evaluator_agent(state)

    # 5. Assemble final markdown
    state.final_markdown = generate_module_overview(
        module_path=state.module_path,
        docs=state.draft_docs,
    )

    # 6. Save to file
    out_path = write_doc_markdown(state.module_path, state.final_markdown)
    print(f"[INFO] Wrote docs to: {out_path}")

    return state
