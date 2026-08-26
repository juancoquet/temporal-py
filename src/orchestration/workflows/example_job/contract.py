"""The ``example_job`` workflow's contract: dispatched by name, id derived from the payload.

Its argument and result types are the domain models, imported from ``src.example``.
"""

from src.example.models import ExampleRequest, ExampleResult
from src.orchestration.contracts import WorkflowContract
from src.orchestration.workflows.names import WorkflowName

EXAMPLE_JOB_WORKFLOW: WorkflowContract[ExampleRequest, ExampleResult] = WorkflowContract(
    name=WorkflowName.EXAMPLE_JOB,
    arg=ExampleRequest,
    out=ExampleResult,
    key=lambda request: f"example-job-{request.work_id}",
)
