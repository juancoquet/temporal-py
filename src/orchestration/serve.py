"""The shared worker entrypoint every unit's ``serve.py`` delegates to.

A worker process's ``serve.py`` is a thin shim: it names its ``build_worker`` and calls :func:`run`.
Connecting the client and running the worker is written here once, not copied into every
``serve.py``. If your app configures logging, do it here too — once, at the entrypoint — rather than
at import (an import-time side effect would trip the workflow sandbox).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.orchestration.client import production_temporal_client

if TYPE_CHECKING:
    from collections.abc import Callable

    from temporalio.client import Client
    from temporalio.worker import Worker


def run(build_worker: Callable[[Client], Worker]) -> None:
    """Connect the client, build the worker, and run it until cancelled."""

    async def _serve() -> None:
        client = await production_temporal_client()
        await build_worker(client).run()

    asyncio.run(_serve())
