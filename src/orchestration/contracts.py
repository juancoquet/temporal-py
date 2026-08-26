"""The generic, import-light contract seam: the base activity and workflow contracts.

A caller — a workflow, or a starter — imports a concrete contract and dispatches by string name with
``result_type``, recovering static typing across the environment boundary without importing the
implementation. The ``name`` is a plain ``str`` so this kit stays app-agnostic; your app defines a
`StrEnum` of names and passes its members here (a `StrEnum` member *is* a ``str``), which gives the
closed, typed, collision-safe set of names at every definition site.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING

from temporalio import workflow

from src.primitives import NOT_GIVEN, FrozenBaseModel, NotGiven, was_given

if TYPE_CHECKING:
    from temporalio.client import Client


class ActivityContract[TIn: FrozenBaseModel, TOut: FrozenBaseModel](FrozenBaseModel):
    """A typed handle to one activity, dispatched by string name across the worker boundary.

    Carries the activity's name, its argument and result types, and its timeout, and derives the
    task queue its dedicated worker polls. :meth:`execute` calls Temporal by name with
    ``result_type`` set, so a workflow recovers a statically-typed result without importing the
    implementation.
    """

    name: str
    arg: type[TIn]
    out: type[TOut]
    start_to_close: timedelta = timedelta(minutes=30)

    @property
    def queue(self) -> str:
        """The task queue this activity's dedicated worker polls."""
        return f"{self.name}_queue"

    async def execute(self, arg: TIn) -> TOut:
        """Dispatch the activity from within a workflow and return its typed result."""
        return self.out.model_validate(
            await workflow.execute_activity(
                self.name,
                arg,
                task_queue=self.queue,
                result_type=self.out,
                start_to_close_timeout=self.start_to_close,
            )
        )


class WorkflowContract[TIn: FrozenBaseModel, TOut: FrozenBaseModel](FrozenBaseModel):
    """A typed handle to one workflow, dispatched by string name.

    Carries the workflow's name, its argument and result types, a ``key`` that derives the workflow
    id (a deduplicating business key) from the payload, and its execution timeout, and derives the
    task queue its worker polls. :meth:`start` launches it from a client (the entrypoint);
    :meth:`execute_as_child` launches it as a child from within another workflow.
    """

    name: str
    arg: type[TIn]
    out: type[TOut]
    key: Callable[[TIn], str]  # derive the workflow id from the payload
    execution_timeout: timedelta = timedelta(hours=1)

    @property
    def queue(self) -> str:
        """The task queue this workflow's worker polls."""
        return f"{self.name}_queue"

    async def execute_as_child(self, arg: TIn, *, workflow_id: str | NotGiven = NOT_GIVEN) -> TOut:
        """Start this workflow as a child from within a parent workflow, and await its result."""
        return self.out.model_validate(
            await workflow.execute_child_workflow(
                self.name,
                arg,
                id=self._wid(arg, workflow_id),
                task_queue=self.queue,
                result_type=self.out,
                execution_timeout=self.execution_timeout,
            )
        )

    async def start(
        self, client: Client, arg: TIn, *, workflow_id: str | NotGiven = NOT_GIVEN
    ) -> TOut:
        """Start this workflow from a client and await its result."""
        return self.out.model_validate(
            await client.execute_workflow(
                self.name,
                arg,
                id=self._wid(arg, workflow_id),
                task_queue=self.queue,
                result_type=self.out,
                execution_timeout=self.execution_timeout,
            )
        )

    def _wid(self, arg: TIn, workflow_id: str | NotGiven) -> str:
        # workflow_id overrides the derived id: to run several workflows of this type for one
        # payload (which would otherwise collide on the same id), or to re-run under a chosen id.
        return workflow_id if was_given(workflow_id) else self.key(arg)
