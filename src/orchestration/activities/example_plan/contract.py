"""The ``example_plan`` activity's contract — the import-light dispatch seam.

The boundary types live in ``models.py`` and are imported here; a workflow imports this contract to
dispatch the activity by name without importing the implementation.
"""

from datetime import timedelta

from src.example.models import ExamplePlan, ExampleRequest
from src.orchestration.activities.names import ActivityName
from src.orchestration.contracts import ActivityContract

EXAMPLE_PLAN_ACTIVITY: ActivityContract[ExampleRequest, ExamplePlan] = ActivityContract(
    name=ActivityName.EXAMPLE_PLAN,
    arg=ExampleRequest,
    out=ExamplePlan,
    start_to_close=timedelta(minutes=2),
)
