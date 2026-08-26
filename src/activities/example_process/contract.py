"""The ``example_process`` activity's contract.

Its argument is the plan's item type, imported from the upstream activity's models; its result type
lives in this activity's ``models.py``.
"""

from src.activities.example_plan.models import ExampleItem
from src.activities.example_process.models import ExampleResult
from src.activities.names import ActivityName
from src.orchestration.contracts import ActivityContract

EXAMPLE_PROCESS_ACTIVITY: ActivityContract[ExampleItem, ExampleResult] = ActivityContract(
    name=ActivityName.EXAMPLE_PROCESS,
    arg=ExampleItem,
    out=ExampleResult,
)
