"""The ``example_plan`` activity's boundary types and contract — the import-light seam.

A real activity's boundary types carry *references* to durable objects (a content hash, a cache key,
an id, a coordinate), never a blob or a heavy derived view. They must import nothing heavy, so the
workflow — which imports this to dispatch — stays light.
"""

from datetime import timedelta

from src.activities.names import ActivityName
from src.orchestration.contracts import ActivityContract
from src.primitives import FrozenBaseModel, NonEmptyStr


class ExampleRequest(FrozenBaseModel):
    """Template activity input."""

    work_id: NonEmptyStr


class ExampleItem(FrozenBaseModel):
    """Template unit of fanned-out work — the plan's items, and the process activity's input."""

    work_id: NonEmptyStr
    index: int


class ExamplePlan(FrozenBaseModel):
    """Template plan — the items a workflow fans out over."""

    items: tuple[ExampleItem, ...]


EXAMPLE_PLAN_ACTIVITY: ActivityContract[ExampleRequest, ExamplePlan] = ActivityContract(
    name=ActivityName.EXAMPLE_PLAN,
    arg=ExampleRequest,
    out=ExamplePlan,
    start_to_close=timedelta(minutes=2),
)
