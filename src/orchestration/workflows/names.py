"""The closed, typed set of workflow names — the string keys that cross the worker boundary."""

import enum


@enum.unique
class WorkflowName(enum.StrEnum):
    """Every workflow, one member each, alphabetical.

    Each member has a matching directory under `src/workflows/`.
    """

    EXAMPLE_JOB = "example_job_workflow"
