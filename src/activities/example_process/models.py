"""Domain models for the ``example_process`` activity.

Its input is the upstream plan's item type (``ExampleItem``), imported from that activity's models —
mirroring how a downstream stage consumes an upstream stage's type.
"""

from src.primitives import FrozenBaseModel, NonEmptyStr


class ExampleResult(FrozenBaseModel):
    """The activity's (and the workflow's) result."""

    work_id: NonEmptyStr
    index: int
