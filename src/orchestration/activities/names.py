"""The closed, typed set of activity names: the string keys that cross the worker boundary."""

import enum


@enum.unique
class ActivityName(enum.StrEnum):
    """Every activity, one member each, alphabetical.

    Each member has a matching directory under `src/activities/` carrying `contract.py`,
    `definition.py`, `worker.py`, and `serve.py`. A `StrEnum` member is a ``str``, so it is passed
    straight to an :class:`~src.orchestration.contracts.ActivityContract`'s ``name``.
    """

    EXAMPLE_PLAN = "example_plan"
    EXAMPLE_PROCESS = "example_process"
