"""Worker entrypoint for the ``example_plan`` activity — its image runs this module.

python -m src.activities.example_plan.serve
"""

import asyncio
import logging

from src.activities.example_plan.worker import build_worker
from src.orchestration.client import build_client

_logger = logging.getLogger(__name__)


async def _serve() -> None:
    client = await build_client()
    worker = build_worker(client)
    _logger.info("starting example-plan worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(_serve())
