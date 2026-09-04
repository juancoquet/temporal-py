import pytest

from src.orchestration.client import TemporalConnection, load_temporal_connection


def test_temporal_connection_uses_local_defaults():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.delenv("TEMPORAL_TARGET", raising=False)
        monkeypatch.delenv("TEMPORAL_NAMESPACE", raising=False)

        assert load_temporal_connection() == TemporalConnection(
            target="localhost:7233",
            namespace="default",
        )


def test_temporal_connection_uses_environment():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("TEMPORAL_TARGET", "temporal.example.test:7233")
        monkeypatch.setenv("TEMPORAL_NAMESPACE", "example")

        assert load_temporal_connection() == TemporalConnection(
            target="temporal.example.test:7233",
            namespace="example",
        )


def test_temporal_connection_uses_explicit_values():
    assert load_temporal_connection(
        target="temporal.example.test:7233",
        namespace="example",
    ) == TemporalConnection(
        target="temporal.example.test:7233",
        namespace="example",
    )
