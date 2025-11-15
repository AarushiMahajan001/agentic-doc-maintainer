from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CodeChunk(BaseModel):
    id: int
    file_path: str
    symbol_name: str
    start_line: int
    end_line: int
    code: str


class DocTaskState(BaseModel):
    module_path: str
    query: Optional[str] = None

    # Use default_factory to avoid mutable default issues
    selected_chunks: List[CodeChunk] = Field(default_factory=list)
    draft_docs: Dict[str, str] = Field(default_factory=dict)
    evaluations: Dict[str, Dict] = Field(default_factory=dict)
    final_markdown: Optional[str] = None
