"""The ``example_process`` activity implementation — a constructor-injected collaborator.

A real activity would import its domain/stage code here (the heavy dependency the worker loads
once); this template injects a trivial in-module collaborator to show the shape.
"""

from dataclasses import dataclass
from typing import Protocol

from temporalio import activity

from src.activities.example_plan.models import ExampleItem
from src.activities.example_process.contract import EXAMPLE_PROCESS_ACTIVITY
from src.activities.example_process.models import ExampleResult


class ExampleService(Protocol):
    """A template for an injected collaborator — e.g. a loaded model or a provider client."""

    async def handle(self, item: ExampleItem) -> ExampleResult: ...


@dataclass
class ExampleActivities:
    """Template for activities sharing one injected collaborator, built once per worker."""

    service: ExampleService

    @activity.defn(name=EXAMPLE_PROCESS_ACTIVITY.name)
    async def example_process(self, item: ExampleItem) -> ExampleResult:
        return await self.service.handle(item)


@dataclass
class _EchoService:
    """A trivial concrete collaborator standing in for a real one in the template."""

    async def handle(self, item: ExampleItem) -> ExampleResult:
        return ExampleResult(work_id=item.work_id, index=item.index)


def production_example_service() -> ExampleService:
    """Build the template collaborator; a real factory wires the stage's dependencies here."""
    return _EchoService()
