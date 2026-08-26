"""The ``example_job`` workflow implementation — orchestration only, no heavy or task imports.

Workflow code stays pure and import-light for determinism: it imports activity *contracts* and calls
them by name, never an implementation, plus the domain models it passes and returns. Where
wall-clock or randomness is needed, use ``workflow.now`` / ``workflow.random`` / ``workflow.uuid4``.
"""

from temporalio import workflow

from src.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY
from src.activities.example_plan.models import ExampleRequest
from src.activities.example_process.contract import EXAMPLE_PROCESS_ACTIVITY
from src.activities.example_process.models import ExampleResult
from src.workflows.example_job.contract import EXAMPLE_JOB_WORKFLOW


@workflow.defn(name=EXAMPLE_JOB_WORKFLOW.name)
class ExampleJob:
    """Template workflow — dispatches its activities through their contracts."""

    @workflow.run
    async def run(self, request: ExampleRequest) -> ExampleResult:
        plan = await EXAMPLE_PLAN_ACTIVITY.execute(request)
        for item in plan.items:
            _ = await EXAMPLE_PROCESS_ACTIVITY.execute(item)
        return ExampleResult(work_id=request.work_id, index=len(plan.items))
