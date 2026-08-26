"""Shared worker-construction helpers, called by each activity's / workflow's ``worker.py``.

Construction lives beside each unit (in its ``worker.py``); these helpers derive the task queue from
the contract, so no worker can be built without one.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from temporalio.worker import Worker

from src.primitives import FrozenBaseModel

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from temporalio.client import Client

    from src.orchestration.contracts import ActivityContract, WorkflowContract

type ActivityImpl[TIn: FrozenBaseModel, TOut: FrozenBaseModel] = Callable[
    [TIn], TOut | Awaitable[TOut]
]


def build_activity_worker[TIn: FrozenBaseModel, TOut: FrozenBaseModel](
    client: Client,
    contract: ActivityContract[TIn, TOut],
    impl: ActivityImpl[TIn, TOut],
    *,
    executor: Executor | None = None,  # required for a sync (e.g. blocking / GPU) activity
) -> Worker:
    """Build the worker for one activity: its queue and the impl."""
    return Worker(
        client,
        task_queue=contract.queue,
        activities=[impl],
        activity_executor=executor,
    )


def build_workflow_worker[TIn: FrozenBaseModel, TOut: FrozenBaseModel](
    client: Client,
    contract: WorkflowContract[TIn, TOut],
    definition: type[object],
) -> Worker:
    """Build the worker for one workflow: its queue and definition (Temporal sandboxes it)."""
    return Worker(
        client,
        task_queue=contract.queue,
        workflows=[definition],
    )
