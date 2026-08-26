"""Worker entrypoint for the ``example_process`` activity — its image runs this module.

python -m src.activities.example_process.serve
"""

import asyncio

from src.activities.example_process.worker import build_worker
from src.orchestration.client import production_temporal_client


async def _serve() -> None:
    await build_worker(await production_temporal_client()).run()


if __name__ == "__main__":
    asyncio.run(_serve())
