from typing import Dict
from groq import Groq

from app.models import DocTaskState
from app.config import GROQ_API_KEY, GROQ_MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

EVAL_SYSTEM_PROMPT = (
    "You are a strict documentation reviewer for Python APIs. "
    "You score docs based on correctness, coverage, clarity, and consistency "
    "with the given code."
)

EVAL_USER_TEMPLATE = (
    "You are given:\n\n"
    "1. The Python code for a function or class.\n"
    "2. The generated documentation in Markdown.\n\n"
    "Please score the documentation on the following 4 criteria from 1 (poor) to 5 (excellent):\n\n"
    "- correctness: does it accurately describe the behavior?\n"
    "- coverage: does it mention key parameters, return value, and side effects?\n"
    "- clarity: is it easy to understand?\n"
    "- consistency: does it avoid inventing parameters/behavior not in the code?\n\n"
    "Respond ONLY as a JSON object with this exact structure:\n\n"
    "{{\n"
    '  "correctness": <int 1-5>,\n'
    '  "coverage": <int 1-5>,\n'
    '  "clarity": <int 1-5>,\n'
    '  "consistency": <int 1-5>,\n'
    '  "overall_score": <int 1-5>\n'
    "}}\n\n"
    "CODE:\n"
    "```python\n"
    "{code}\n"
    "```\n\n"
    "DOC:\n"
    "```markdown\n"
    "{doc}\n"
    "```"
)


def _evaluate_doc_with_groq(code: str, doc: str) -> Dict:
    user_prompt = EVAL_USER_TEMPLATE.format(code=code, doc=doc)

    completion = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {"role": "system", "content": EVAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )

    content = completion.choices[0].message.content

    import json

    try:
        scores = json.loads(content)
    except json.JSONDecodeError:
        scores = {
            "correctness": None,
            "coverage": None,
            "clarity": None,
            "consistency": None,
            "overall_score": None,
            "raw_response": content,
        }
    return scores


def run_evaluator_agent(state: DocTaskState) -> DocTaskState:
    """
    Evaluate each draft doc using LLM-as-judge via Groq.
    """
    evaluations: Dict[str, Dict] = {}

    for chunk in state.selected_chunks:
        symbol = chunk.symbol_name
        doc = state.draft_docs.get(symbol)
        if not doc:
            continue

        scores = _evaluate_doc_with_groq(chunk.code, doc)
        evaluations[symbol] = scores

    state.evaluations = evaluations
    return state
