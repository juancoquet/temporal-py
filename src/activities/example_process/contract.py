"""The ``example_process`` activity's contract.

Its argument is the plan's item type, imported from the upstream activity's models; its result type
lives in this activity's ``models.py``.
"""

from src.activities.names import ActivityName
from src.example.models import ExampleItem, ExampleResult
from src.orchestration.contracts import ActivityContract

EXAMPLE_PROCESS_ACTIVITY: ActivityContract[ExampleItem, ExampleResult] = ActivityContract(
    name=ActivityName.EXAMPLE_PROCESS,
    arg=ExampleItem,
    out=ExampleResult,
)
