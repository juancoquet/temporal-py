"""Worker entrypoint for the ``example_job`` workflow — its image runs this module.

python -m src.workflows.example_job.serve
"""

import asyncio

from src.orchestration.client import production_temporal_client
from src.workflows.example_job.worker import build_worker


async def _serve() -> None:
    await build_worker(await production_temporal_client()).run()


if __name__ == "__main__":
    asyncio.run(_serve())
