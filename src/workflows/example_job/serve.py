"""Worker entrypoint for the ``example_job`` workflow — its image runs this module.

python -m src.workflows.example_job.serve
"""

import asyncio
import logging

from src.orchestration.client import build_client
from src.workflows.example_job.worker import build_worker

_logger = logging.getLogger(__name__)


async def _serve() -> None:
    client = await build_client()
    worker = build_worker(client)
    _logger.info("starting example-job workflow worker")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(_serve())
