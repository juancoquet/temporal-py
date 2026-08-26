"""How the ``example_process`` worker is built: collaborator injected once, colocated here."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.example.service import production_example_service
from src.orchestration.activities.example_process.contract import EXAMPLE_PROCESS_ACTIVITY
from src.orchestration.activities.example_process.definition import ExampleActivities
from src.orchestration.worker import build_activity_worker

if TYPE_CHECKING:
    from temporalio.client import Client
    from temporalio.worker import Worker


def build_worker(client: Client) -> Worker:
    """Build the worker that serves the ``example_process`` activity."""
    activities = ExampleActivities(service=production_example_service())
    return build_activity_worker(client, EXAMPLE_PROCESS_ACTIVITY, activities.example_process)
