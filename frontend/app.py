"""
Simple Streamlit frontend for the Agentic Documentation & Code Maintainer.

Usage:
    cd /Users/aarushimahajan/Desktop/agentic-doc-maintainer
    source .venv/bin/activate
    streamlit run frontend/app.py
"""

import sys
from pathlib import Path
from typing import Optional

import streamlit as st

# --- Make sure we can import the app package from the project root ---
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.orchestration.graph import run_documentation_pipeline
from app.config import DOCS_DIR


def get_doc_path(module_path: str) -> Path:
    """
    Reconstruct the markdown doc path the same way the backend does:
    replace slashes in module_path with underscores and append .md.
    """
    safe_name = module_path.replace("/", "_")
    return DOCS_DIR / f"{safe_name}.md"


def main():
    st.set_page_config(
        page_title="Agentic Code & Documentation Maintainer",
        layout="wide",
    )

    st.title("Agentic Code and Documentation Maintainer")

    st.markdown(
        """
This UI lets you run the documentation pipeline on any Python module that lives
under `data/repo/`.

**Steps:**
1. Put your GitHub repo or local project under `data/repo/`.
2. Run `python scripts/ingest_repo.py` to build the index.
3. Enter the module path below and click “Run pipeline”.
        """
    )

    st.sidebar.header("Pipeline inputs")

    default_module = (
        "Calgary_Crime_Data_Analysis_and_Neural_Network_Prediction/"
        "Calgary_Crime_Data_Analysis_and_Neural_Network_Prediction.py"
    )

    module_path = st.sidebar.text_input(
        "Module path (relative to data/repo)",
        value=default_module,
        help="Example: my_repo/src/model.py or repo_name/main.py",
    )

    query: Optional[str] = st.sidebar.text_input(
        "Optional focus query",
        value="sequence creation for crime time series",
        help="Optional hint about what kind of functionality is most important.",
    )

    run_button = st.sidebar.button("Run pipeline")

    if run_button:
        if not module_path.strip():
            st.error("Please enter a module path.")
            return

        st.info(f"Running documentation pipeline for `{module_path}`...")
        with st.spinner("Thinking, searching, and writing docs..."):
            try:
                state = run_documentation_pipeline(
                    module_path=module_path,
                    query=query or None,
                )
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                return

        st.success("Pipeline finished.")

        # --- Show documentation ---
        doc_path = get_doc_path(module_path)
        st.subheader("Generated documentation")

        if doc_path.exists():
            try:
                doc_text = doc_path.read_text()
            except Exception as e:
                st.error(f"Could not read documentation file: {e}")
                doc_text = ""
        else:
            st.warning(
                f"Expected documentation at `{doc_path}`, but file does not exist. "
                "Showing nothing for now."
            )
            doc_text = ""

        if doc_text:
            st.markdown(doc_text)
        else:
            st.write("No documentation content available.")

        # --- Show evaluation scores ---
        st.subheader("Evaluation scores (LLM as judge)")

        evaluations = getattr(state, "evaluations", {}) or {}
        if not evaluations:
            st.write("No evaluations were returned by the pipeline.")
        else:
            for symbol, scores in evaluations.items():
                st.markdown(f"**Function or symbol:** `{symbol}`")
                st.json(scores)
    else:
        st.info("Enter a module path in the sidebar and click 'Run pipeline'.")


if __name__ == "__main__":
    main()

