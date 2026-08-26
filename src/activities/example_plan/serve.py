"""Worker entrypoint for the ``example_plan`` activity — its image runs this module.

python -m src.activities.example_plan.serve
"""

from src.activities.example_plan.worker import build_worker
from src.orchestration.serve import run

if __name__ == "__main__":
    run(build_worker)
