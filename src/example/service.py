"""An implementation of the example service port.

The implementation satisfies :class:`~src.example.ports.ExampleService` *structurally* — it has the
right method and never imports or inherits the protocol. Only the factory's return type names the
port, so callers depend on the interface, not this class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.example.models import ExampleItem, ExampleResult

if TYPE_CHECKING:
    from src.example.ports import ExampleService


class _EchoService:
    """A trivial implementation standing in for real business logic."""

    async def handle(self, item: ExampleItem) -> ExampleResult:
        return ExampleResult(work_id=item.work_id, index=item.index)


def production_example_service() -> ExampleService:
    """Build the production service; a real factory wires its dependencies here."""
    return _EchoService()
