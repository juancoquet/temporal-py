"""A trivial implementation of the example service port.

``EchoService`` satisfies :class:`~src.example.ports.ExampleService` *structurally*: it has the
right method and never imports or inherits the protocol. Consumers depend on the port; this module
just provides a concrete implementation and a factory for it.
"""

from src.example.models import ExampleItem, ExampleResult


class EchoService:
    """A trivial implementation standing in for real business logic."""

    async def handle(self, item: ExampleItem) -> ExampleResult:
        return ExampleResult(work_id=item.work_id, index=item.index)


def production_example_service() -> EchoService:
    """Build the production service; a real factory wires its dependencies here."""
    return EchoService()
