"""Domain models for the ``example_plan`` activity.

In a real service these are your domain types (or lightweight references to them) — they live in a
models module and are *imported* by the contract, the definition, and any workflow that dispatches
the activity, never defined inline in the contract. Keep them light and reference-only (ids, hashes,
keys, coordinates), so the workflow that imports the contract stays free of heavy dependencies.
"""

from src.primitives import FrozenBaseModel, NonEmptyStr


class ExampleRequest(FrozenBaseModel):
    """The activity's input."""

    work_id: NonEmptyStr


class ExampleItem(FrozenBaseModel):
    """A unit of fanned-out work — the plan's items, and the process activity's input."""

    work_id: NonEmptyStr
    index: int


class ExamplePlan(FrozenBaseModel):
    """The plan a workflow fans out over."""

    items: tuple[ExampleItem, ...]
