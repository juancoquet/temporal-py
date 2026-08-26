"""Domain logic for planning the units of work a job fans out over."""

from src.example.models import ExampleItem, ExamplePlan, ExampleRequest


def build_plan(request: ExampleRequest) -> ExamplePlan:
    """Build the plan for a request: the items to fan out over."""
    return ExamplePlan(
        items=(
            ExampleItem(work_id=request.work_id, index=0),
            ExampleItem(work_id=request.work_id, index=1),
        )
    )
