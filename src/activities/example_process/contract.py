"""The ``example_process`` activity's boundary types and contract.

Its input is the plan's item type (``ExampleItem``), imported from the upstream activity's contract
— mirroring how a downstream stage's input is an upstream stage's output.
"""

from src.activities.example_plan.contract import ExampleItem
from src.activities.names import ActivityName
from src.orchestration.contracts import ActivityContract
from src.primitives import FrozenBaseModel, NonEmptyStr


class ExampleResult(FrozenBaseModel):
    """Template activity and workflow result."""

    work_id: NonEmptyStr
    index: int


EXAMPLE_PROCESS_ACTIVITY: ActivityContract[ExampleItem, ExampleResult] = ActivityContract(
    name=ActivityName.EXAMPLE_PROCESS,
    arg=ExampleItem,
    out=ExampleResult,
)
