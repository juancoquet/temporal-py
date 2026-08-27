"""Building the Temporal client shared by workers and workflow starters."""

from temporalio.client import Client

from src.orchestration.converter import orchestration_data_converter

# Hardcoded: this is example code and none of it is sensitive. A real app reads these from the
# environment. The data converter carries FrozenBaseModel payloads across the wire with their types
# intact and turns malformed typed payloads into terminal failures.
_TARGET = "localhost:7233"
_NAMESPACE = "default"


async def build_client() -> Client:
    """Connect a Temporal client with the orchestration layer's payload policy."""
    return await Client.connect(
        _TARGET,
        namespace=_NAMESPACE,
        data_converter=orchestration_data_converter,
    )
