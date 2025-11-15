import argparse
from pprint import pprint
import sys
import os

# --- Make sure the project root is on sys.path ---
# This lets us do "from app...." imports even when
# this script lives inside the "scripts/" folder.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.orchestration.graph import run_documentation_pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "module_path",
        help="Path to module relative to data/repo, e.g. Deep-learning-based-mobile-tracking/utils.py",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional natural language focus, e.g. 'document main tracking APIs'",
    )
    args = parser.parse_args()

    state = run_documentation_pipeline(args.module_path, query=args.query)

    print("\n" + "#" * 80)
    print("FINAL DOCUMENTATION")
    print("#" * 80 + "\n")
    print(state.final_markdown)

    print("\n" + "#" * 80)
    print("EVALUATIONS")
    print("#" * 80 + "\n")
    pprint(state.evaluations)


if __name__ == "__main__":
    main()
