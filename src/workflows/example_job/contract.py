"""The ``example_job`` workflow's contract — dispatched by name, id derived from the payload.

Its argument and result types are the activities' domain models, imported from their models modules.
"""

from src.activities.example_plan.models import ExampleRequest
from src.activities.example_process.models import ExampleResult
from src.orchestration.contracts import WorkflowContract, WorkflowId
from src.workflows.names import WorkflowName

EXAMPLE_JOB_WORKFLOW: WorkflowContract[ExampleRequest, ExampleResult] = WorkflowContract(
    name=WorkflowName.EXAMPLE_JOB,
    arg=ExampleRequest,
    out=ExampleResult,
    key=lambda request: WorkflowId.from_identifier(request.work_id),
)
