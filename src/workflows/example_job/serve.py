"""Worker entrypoint for the ``example_job`` workflow — its image runs this module.

python -m src.workflows.example_job.serve
"""

from src.orchestration.serve import run
from src.workflows.example_job.worker import build_worker

if __name__ == "__main__":
    run(build_worker)
