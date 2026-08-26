"""The ``example_plan`` activity: the Temporal adapter over the domain's ``build_plan``.

The activity holds no logic; it calls the domain function and returns its result. The work lives in
``src.example``, not here.
"""

from temporalio import activity

from src.example.models import ExamplePlan, ExampleRequest
from src.example.plan import build_plan
from src.orchestration.activities.example_plan.contract import EXAMPLE_PLAN_ACTIVITY


@activity.defn(name=EXAMPLE_PLAN_ACTIVITY.name)
async def example_plan(request: ExampleRequest) -> ExamplePlan:
    return build_plan(request)
