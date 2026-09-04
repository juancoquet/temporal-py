import pytest

from src.orchestration.client import TemporalConnection, load_temporal_connection


@pytest.mark.small
def test_temporal_connection_uses_local_defaults():
    assert load_temporal_connection({}) == TemporalConnection(
        target="localhost:7233",
        namespace="default",
    )


@pytest.mark.small
def test_temporal_connection_uses_environment():
    assert load_temporal_connection(
        {
            "TEMPORAL_TARGET": "temporal.example.test:7233",
            "TEMPORAL_NAMESPACE": "example",
        }
    ) == TemporalConnection(
        target="temporal.example.test:7233",
        namespace="example",
    )
