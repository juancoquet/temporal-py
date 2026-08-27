"""Malformed activity and workflow inputs fail once as terminal application errors."""

from contextlib import AsyncExitStack
from datetime import timedelta

import pytest
from temporalio import workflow
from temporalio.client import WorkflowFailureError
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError, RetryState
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.example.models import ExamplePlan, ExampleResult
from src.orchestration.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY
from src.orchestration.activities.example_plan.worker import build_worker as build_plan_worker
from src.orchestration.converter import orchestration_data_converter
from src.orchestration.workflows.example_job.contract import EXAMPLE_JOB_WORKFLOW
from src.orchestration.workflows.example_job.worker import build_worker as build_job_worker

_MALFORMED_ACTIVITY_WORKFLOW = "malformed_activity_test_workflow"
_MALFORMED_ACTIVITY_QUEUE = f"{_MALFORMED_ACTIVITY_WORKFLOW}_queue"


@pytest.mark.medium
async def test_malformed_workflow_input_is_non_retryable():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=orchestration_data_converter
    ) as env:
        async with build_job_worker(env.client):
            with pytest.raises(WorkflowFailureError) as raised:
                await env.client.execute_workflow(
                    EXAMPLE_JOB_WORKFLOW.name,
                    {},
                    id="malformed-workflow-input",
                    task_queue=EXAMPLE_JOB_WORKFLOW.queue,
                    result_type=ExampleResult,
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )

    error = raised.value.cause
    assert isinstance(error, ApplicationError)
    assert error.type == "ValidationError"
    assert error.non_retryable


@pytest.mark.medium
async def test_malformed_activity_input_is_non_retryable():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=orchestration_data_converter
    ) as env:
        async with AsyncExitStack() as stack:
            _ = await stack.enter_async_context(build_plan_worker(env.client))
            _ = await stack.enter_async_context(
                Worker(
                    env.client,
                    task_queue=_MALFORMED_ACTIVITY_QUEUE,
                    workflows=[_MalformedActivityWorkflow],
                )
            )
            with pytest.raises(WorkflowFailureError) as raised:
                await env.client.execute_workflow(
                    _MALFORMED_ACTIVITY_WORKFLOW,
                    id="malformed-activity-input",
                    task_queue=_MALFORMED_ACTIVITY_QUEUE,
                )

    activity_error = raised.value.cause
    assert isinstance(activity_error, ActivityError)
    assert activity_error.retry_state is RetryState.NON_RETRYABLE_FAILURE
    error = activity_error.cause
    assert isinstance(error, ApplicationError)
    assert error.type == "ValidationError"
    assert error.non_retryable


@workflow.defn(name=_MALFORMED_ACTIVITY_WORKFLOW, sandboxed=False)
class _MalformedActivityWorkflow:
    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            EXAMPLE_PLAN_ACTIVITY.name,
            {},
            task_queue=EXAMPLE_PLAN_ACTIVITY.queue,
            result_type=ExamplePlan,
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
