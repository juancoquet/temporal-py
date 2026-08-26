"""How the ``example_job`` workflow worker is built — colocated with the workflow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.orchestration.worker import build_workflow_worker
from src.workflows.example_job.contract import EXAMPLE_JOB_WORKFLOW
from src.workflows.example_job.definition import ExampleJob

if TYPE_CHECKING:
    from temporalio.client import Client
    from temporalio.worker import Worker


def build_worker(client: Client) -> Worker:
    """Build the worker that serves the ``example_job`` workflow."""
    return build_workflow_worker(client, EXAMPLE_JOB_WORKFLOW, ExampleJob)
