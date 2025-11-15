from app.models import DocTaskState


def plan_doc_task(state: DocTaskState) -> DocTaskState:
    """
    Planner agent.

    For now this is a trivial planner:
    - It just returns the state unchanged.

    Later you can make this smarter, e.g.:
    - Decide whether to focus on a specific module region
    - Filter to public APIs only
    - Choose different strategies based on `state.query`
    """
    return state
