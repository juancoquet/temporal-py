"""The ``example_plan`` activity implementation — a free-function activity, no collaborator.

A real activity's definition imports its domain/stage code here (often heavy). Because a worker
image imports only its own activity's ``definition``, those imports never meet another activity's.
"""

from temporalio import activity

from src.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY
from src.example.models import ExampleItem, ExamplePlan, ExampleRequest


@activity.defn(name=EXAMPLE_PLAN_ACTIVITY.name)
async def example_plan(request: ExampleRequest) -> ExamplePlan:
    """Template free-function activity — returns a small fixed plan to fan out over."""
    return ExamplePlan(
        items=(
            ExampleItem(work_id=request.work_id, index=0),
            ExampleItem(work_id=request.work_id, index=1),
        )
    )
