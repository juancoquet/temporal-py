"""The contracts' pure behaviour: queue derivation, id derivation, and example wiring."""

import pytest

from src.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY
from src.activities.example_plan.models import ExamplePlan, ExampleRequest
from src.activities.example_process.contract import EXAMPLE_PROCESS_ACTIVITY
from src.activities.example_process.models import ExampleResult
from src.activities.names import ActivityName
from src.orchestration.contracts import WorkflowId
from src.workflows.example_job.contract import EXAMPLE_JOB_WORKFLOW
from src.workflows.names import WorkflowName


@pytest.mark.small
def test_activity_queue_is_derived_from_the_name():
    assert EXAMPLE_PLAN_ACTIVITY.queue == "example_plan_queue"
    assert EXAMPLE_PLAN_ACTIVITY.name == ActivityName.EXAMPLE_PLAN


@pytest.mark.small
def test_workflow_queue_is_derived_from_the_name():
    assert EXAMPLE_JOB_WORKFLOW.queue == "example_job_workflow_queue"
    assert EXAMPLE_JOB_WORKFLOW.name == WorkflowName.EXAMPLE_JOB


@pytest.mark.small
def test_activity_contract_carries_its_argument_and_result_types():
    assert EXAMPLE_PLAN_ACTIVITY.arg is ExampleRequest
    assert EXAMPLE_PLAN_ACTIVITY.out is ExamplePlan


@pytest.mark.small
def test_every_activity_name_has_a_distinct_queue():
    contracts = (EXAMPLE_PLAN_ACTIVITY, EXAMPLE_PROCESS_ACTIVITY)
    assert len({contract.queue for contract in contracts}) == len(contracts)


@pytest.mark.small
def test_workflow_id_is_derived_from_the_payload_by_default():
    derived = EXAMPLE_JOB_WORKFLOW.key(ExampleRequest(work_id="doc-1"))
    assert derived == WorkflowId.from_identifier("doc-1")
    assert str(derived) == "wf-doc-1"


@pytest.mark.small
def test_an_explicit_workflow_id_overrides_the_derived_one():
    request = ExampleRequest(work_id="doc-1")
    chosen = WorkflowId.from_identifier("doc-1-rerun")
    # _wid is the internal seam start()/execute_as_child() use to choose the id.
    assert EXAMPLE_JOB_WORKFLOW._wid(request, chosen) == chosen  # noqa: SLF001


@pytest.mark.small
def test_example_result_carries_the_process_count():
    # ExampleResult is the process activity's and the workflow's shared result type.
    assert ExampleResult(work_id="doc-1", index=2).index == 2
