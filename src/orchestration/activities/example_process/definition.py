"""The ``example_process`` activity: the Temporal adapter over the example domain service.

The activity holds no business logic: it injects the domain service (from ``src.example``, built
once per worker) and calls it. The heavy/domain code lives in ``src.example``, not here.
"""

from dataclasses import dataclass

from temporalio import activity

from src.example.models import ExampleItem, ExampleResult
from src.example.ports import ExampleService
from src.orchestration.activities.example_process.contract import EXAMPLE_PROCESS_ACTIVITY


@dataclass
class ExampleActivities:
    """Activities sharing one injected collaborator, built once per worker."""

    service: ExampleService

    @activity.defn(name=EXAMPLE_PROCESS_ACTIVITY.name)
    async def example_process(self, item: ExampleItem) -> ExampleResult:
        return await self.service.handle(item)
