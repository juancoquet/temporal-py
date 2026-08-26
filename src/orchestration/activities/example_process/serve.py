"""Worker entrypoint for the ``example_process`` activity: its image runs this module.

python -m src.orchestration.activities.example_process.serve
"""

import asyncio
import logging

from src.orchestration.activities.example_process.worker import build_worker
from src.orchestration.client import build_client

_logger = logging.getLogger(__name__)


async def _serve() -> None:
    client = await build_client()
    worker = build_worker(client)
    _logger.info("starting example-process worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(_serve())
