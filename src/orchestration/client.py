"""Building the Temporal client shared by workers and workflow starters."""

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from src.config.temporal import TemporalConfig, production_temporal_config
from src.primitives import NOT_GIVEN, NotGiven, was_given


async def build_client(config: TemporalConfig | NotGiven = NOT_GIVEN) -> Client:
    """Connect a Temporal client that serialises payloads through pydantic.

    The pydantic data converter carries :class:`~src.primitives.FrozenBaseModel` arguments and
    results across the wire with their types intact, so the typed contracts recover static typing on
    the far side of the environment boundary.

    Args:
        config: Connection details; defaults to the process environment's.
    """
    resolved = config if was_given(config) else production_temporal_config()
    return await Client.connect(
        resolved.target,
        namespace=resolved.namespace,
        data_converter=pydantic_data_converter,
    )
