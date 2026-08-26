"""Worker entrypoint for the ``example_process`` activity — its image runs this module.

python -m src.activities.example_process.serve
"""

from src.activities.example_process.worker import build_worker
from src.orchestration.serve import run

if __name__ == "__main__":
    run(build_worker)
