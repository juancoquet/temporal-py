"""End-to-end: the example workflow runs across per-activity queues under a real (in-memory) server.

Starts Temporal's in-memory time-skipping test server (a one-time binary fetch on first run), stands
up each unit's worker, and runs the workflow to completion.
"""

from contextlib import AsyncExitStack

from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment

from src.activities.example_plan.worker import build_worker as build_plan_worker
from src.activities.example_process.worker import build_worker as build_process_worker
from src.example.models import ExampleRequest
from src.workflows.example_job.contract import EXAMPLE_JOB_WORKFLOW
from src.workflows.example_job.worker import build_worker as build_job_worker


async def test_example_job_runs_end_to_end():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        async with AsyncExitStack() as stack:
            for build in (build_plan_worker, build_process_worker, build_job_worker):
                _ = await stack.enter_async_context(build(env.client))
            # workflow_id omitted -> derived from the payload via the contract's key.
            result = await EXAMPLE_JOB_WORKFLOW.start(env.client, ExampleRequest(work_id="doc-1"))

    assert result.work_id == "doc-1"
    assert result.index == 2  # the plan fanned out two items, each processed
