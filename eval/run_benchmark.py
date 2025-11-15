"""
Run a small benchmark over multiple modules using the agentic documentation pipeline.

It reads eval/tasks.yaml, where each task looks like:

- name: "Calgary crime sequences"
  module_path: "Calgary_Crime_Data_Analysis_and_Neural_Network_Prediction/Calgary_Crime_Data_Analysis_and_Neural_Network_Prediction.py"
  query: "crime time series sequence creation"    # optional

For each task, we:
  - run the documentation pipeline
  - collect evaluator scores for all functions in that module
  - report per-task and overall averages
"""

import os
import sys
from pathlib import Path
import statistics
import json

import yaml  # pip install pyyaml

# --- Make sure we can import the app package ---
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.orchestration.graph import run_documentation_pipeline


def load_tasks(tasks_path: Path):
    if not tasks_path.exists():
        raise FileNotFoundError(f"tasks.yaml not found at {tasks_path}")
    with tasks_path.open("r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("tasks.yaml must be a list of task objects")
    return data


def summarize_scores(all_scores):
    """
    all_scores: list of dicts of the form
      {
        "task_name": ...,
        "symbol": ...,
        "scores": { "correctness": int, "coverage": int, ... }
      }
    """
    if not all_scores:
        print("No scores collected.")
        return

    # Flatten metrics
    metrics = ["correctness", "coverage", "clarity", "consistency", "overall_score"]
    metric_values = {m: [] for m in metrics}

    for entry in all_scores:
        scores = entry["scores"]
        for m in metrics:
            val = scores.get(m)
            if isinstance(val, (int, float)):
                metric_values[m].append(val)

    print("\n==================== OVERALL AVERAGE SCORES ====================")
    for m in metrics:
        vals = metric_values[m]
        if vals:
            avg = statistics.mean(vals)
            print(f"{m:12s}: {avg:.2f} over {len(vals)} samples")
        else:
            print(f"{m:12s}: no data")


def main():
    tasks_path = CURRENT_DIR / "tasks.yaml"
    tasks = load_tasks(tasks_path)

    all_scores = []

    print(f"[INFO] Loaded {len(tasks)} tasks from {tasks_path}\n")

    for task in tasks:
        name = task.get("name", "unnamed_task")
        module_path = task["module_path"]
        query = task.get("query")

        print("==============================================================")
        print(f"[TASK] {name}")
        print(f"[TASK] module_path = {module_path}")
        if query:
            print(f"[TASK] query       = {query}")
        print("==============================================================")

        # Run the full agentic pipeline
        state = run_documentation_pipeline(module_path=module_path, query=query)

        # state.evaluations is expected to be: { symbol_name: score_dict }
        evaluations = getattr(state, "evaluations", {}) or {}

        if not evaluations:
            print("[WARN] No evaluations found for this task.\n")
            continue

        print("\nPer-function scores:")
        for symbol, scores in evaluations.items():
            print(f"- {symbol}: {json.dumps(scores)}")
            all_scores.append(
                {
                    "task_name": name,
                    "symbol": symbol,
                    "scores": scores,
                }
            )

        print()  # spacing

    summarize_scores(all_scores)


if __name__ == "__main__":
    main()
