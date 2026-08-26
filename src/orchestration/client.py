"""Building the Temporal client shared by workers and workflow starters."""

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

# Hardcoded: this is example code and none of it is sensitive. A real app reads these from the
# environment. The pydantic data converter carries FrozenBaseModel payloads across the wire with
# their types intact, so the typed contracts recover static typing on the far side.
_TARGET = "localhost:7233"
_NAMESPACE = "default"


async def build_client() -> Client:
    """Connect a Temporal client that serialises payloads through pydantic."""
    return await Client.connect(
        _TARGET,
        namespace=_NAMESPACE,
        data_converter=pydantic_data_converter,
    )
