"""Building the Temporal client shared by workers and workflow starters."""

import os

from temporalio.client import Client

from src.orchestration.converter import orchestration_data_converter
from src.primitives import FrozenBaseModel, NonEmptyStr

_DEFAULT_TARGET = "localhost:7233"
_DEFAULT_NAMESPACE = "default"
_TARGET_ENV = "TEMPORAL_TARGET"
_NAMESPACE_ENV = "TEMPORAL_NAMESPACE"


class TemporalConnection(FrozenBaseModel):
    """The address and namespace a client uses to reach Temporal."""

    target: NonEmptyStr
    namespace: NonEmptyStr


def load_temporal_connection(
    environment: dict[str, str] | None = None,
) -> TemporalConnection:
    """Load connection settings, retaining useful local-development defaults."""
    source = os.environ if environment is None else environment
    target = source.get(_TARGET_ENV, _DEFAULT_TARGET)
    namespace = source.get(_NAMESPACE_ENV, _DEFAULT_NAMESPACE)
    return TemporalConnection(target=target, namespace=namespace)


async def build_client(connection: TemporalConnection | None = None) -> Client:
    """Connect a Temporal client with the orchestration layer's payload policy."""
    resolved = load_temporal_connection() if connection is None else connection
    return await Client.connect(
        resolved.target,
        namespace=resolved.namespace,
        data_converter=orchestration_data_converter,
    )
