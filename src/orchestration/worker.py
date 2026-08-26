"""Shared worker-construction helpers, called by each activity's / workflow's ``worker.py``.

Construction lives beside each unit (in its ``worker.py``); these helpers keep the Temporal wiring —
the task queue, the ``PanicInterceptor`` on every activity, the sandboxed runner on every workflow —
uniform and in one place, so no worker can be built without them.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from src.orchestration.interceptor import PanicInterceptor
from src.primitives import FrozenBaseModel

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from temporalio.client import Client

    from src.orchestration.contracts import ActivityContract, WorkflowContract

type ActivityImpl[TIn: FrozenBaseModel, TOut: FrozenBaseModel] = Callable[
    [TIn], TOut | Awaitable[TOut]
]

# The workflow sandbox is left on (it catches accidental non-determinism in workflow code). If
# importing your app package under the sandbox trips on an import-time side effect the sandbox
# rejects (e.g. logging setup that touches `random`), pass *only* that module through here —
# `SandboxRestrictions.default.with_passthrough_modules("your.module")` — so the workflow
# definitions themselves stay sandboxed. The standing determinism gate is a replay test, not this
# import sandbox.
_WORKFLOW_RUNNER = SandboxedWorkflowRunner(restrictions=SandboxRestrictions.default)


def build_activity_worker[TIn: FrozenBaseModel, TOut: FrozenBaseModel](
    client: Client,
    contract: ActivityContract[TIn, TOut],
    impl: ActivityImpl[TIn, TOut],
    *,
    executor: Executor | None = None,  # required for a sync (e.g. blocking / GPU) activity
) -> Worker:
    """Build the worker for one activity — its queue, the impl, and the Panic seam."""
    return Worker(
        client,
        task_queue=contract.queue,
        activities=[impl],
        interceptors=[PanicInterceptor()],
        activity_executor=executor,
    )


def build_workflow_worker[TIn: FrozenBaseModel, TOut: FrozenBaseModel](
    client: Client,
    contract: WorkflowContract[TIn, TOut],
    definition: type[object],
) -> Worker:
    """Build the worker for one workflow — its queue, the definition, and the sandbox runner."""
    return Worker(
        client,
        task_queue=contract.queue,
        workflows=[definition],
        workflow_runner=_WORKFLOW_RUNNER,
    )
