"""The example domain service — a port and a trivial implementation.

In a real app this is your business logic: a loaded model, a provider client, a database gateway.
It knows nothing about Temporal. The ``example_process`` activity injects it (built once per worker)
and calls it; swapping the implementation never touches the orchestration layer.
"""

from dataclasses import dataclass
from typing import Protocol

from src.example.models import ExampleItem, ExampleResult


class ExampleService(Protocol):
    """The port the process activity depends on — an injected collaborator."""

    async def handle(self, item: ExampleItem) -> ExampleResult: ...


@dataclass
class _EchoService:
    """A trivial implementation standing in for real business logic."""

    async def handle(self, item: ExampleItem) -> ExampleResult:
        return ExampleResult(work_id=item.work_id, index=item.index)


def production_example_service() -> ExampleService:
    """Build the production service; a real factory wires its dependencies here."""
    return _EchoService()
