"""How the ``example_plan`` worker is built: this activity's construction, colocated with it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.orchestration.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY
from src.orchestration.activities.example_plan.definition import example_plan
from src.orchestration.worker import build_activity_worker

if TYPE_CHECKING:
    from temporalio.client import Client
    from temporalio.worker import Worker


def build_worker(client: Client) -> Worker:
    """Build the worker that serves the ``example_plan`` activity."""
    return build_activity_worker(client, EXAMPLE_PLAN_ACTIVITY, example_plan)
