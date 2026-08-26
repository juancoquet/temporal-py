"""The ports the example domain exposes — the interfaces its consumers depend on."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.example.models import ExampleItem, ExampleResult


class ExampleService(Protocol):
    """The port the process activity depends on — an injected collaborator."""

    async def handle(self, item: ExampleItem) -> ExampleResult: ...
