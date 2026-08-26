"""Domain models for the example service.

Light, reference-only value types (ids, hashes, keys, coordinates in a real app), imported by the
activity contracts, definitions, and the workflow. They live here, in the domain package, not in the
orchestration adapters.
"""

from src.primitives import FrozenBaseModel, NonEmptyStr


class ExampleRequest(FrozenBaseModel):
    """The job's input."""

    work_id: NonEmptyStr


class ExampleItem(FrozenBaseModel):
    """A unit of fanned-out work: the plan's items, and the process step's input."""

    work_id: NonEmptyStr
    index: int


class ExamplePlan(FrozenBaseModel):
    """The plan the workflow fans out over."""

    items: tuple[ExampleItem, ...]


class ExampleResult(FrozenBaseModel):
    """The process step's, and the workflow's, result."""

    work_id: NonEmptyStr
    index: int
