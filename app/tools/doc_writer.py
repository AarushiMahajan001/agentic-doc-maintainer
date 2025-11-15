from typing import Dict
import os

from groq import Groq

from app.models import CodeChunk
from app.config import GROQ_API_KEY, GROQ_MODEL_NAME

# Initialize Groq client once
client = Groq(api_key=GROQ_API_KEY)

DOC_SYSTEM_PROMPT = (
    "You are a senior Python library maintainer. "
    "You write precise, concise API documentation for functions and classes."
)

DOC_USER_TEMPLATE = """Write documentation for the following Python function or class.

Requirements:
- Start with a 2–3 line high-level summary.
- Then add sections: **Parameters**, **Returns**, and **Notes** (if needed).
- Use clear, concise language.
- Do NOT change the logic or invent parameters that do not exist.

Return documentation in Markdown format only.

CODE:
```python
{code}
```"""


def _chat_with_groq(system_prompt: str, user_prompt: str) -> str:
    """
    Helper to call Groq Chat Completions and return the text content.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    chat_completion = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # You can tweak temperature if you want more/less creativity
        temperature=0.2,
    )

    return chat_completion.choices[0].message.content


def generate_doc_for_chunk(chunk: CodeChunk) -> str:
    """
    Generate Markdown documentation for a single function/class CodeChunk
    using Groq.
    """
    user_prompt = DOC_USER_TEMPLATE.format(code=chunk.code)
    doc_markdown = _chat_with_groq(DOC_SYSTEM_PROMPT, user_prompt)
    return doc_markdown


def generate_module_overview(module_path: str, docs: Dict[str, str]) -> str:
    """
    Combine per-symbol docs into a single markdown module doc.
    docs: mapping of symbol_name -> markdown
    """
    header = f"# Module `{module_path}`\n\n"
    body = ""
    for symbol_name, doc in docs.items():
        body += f"## {symbol_name}\n\n{doc}\n\n"
    return header + body
