from pathlib import Path
from app.config import DOCS_DIR


def write_doc_markdown(module_path: str, content: str) -> Path:
    """
    Write docs to data/docs/<safe_module_name>.md and return the path.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Turn "Deep-learning-based-mobile-tracking/utils.py" into a safe filename
    safe_name = module_path.replace("/", "_").replace("\\", "_")
    out_path = DOCS_DIR / f"{safe_name}.md"

    out_path.write_text(content)
    return out_path
