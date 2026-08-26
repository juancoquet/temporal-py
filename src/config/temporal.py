"""Temporal control-plane connection configuration."""

import os
from functools import cache

from pydantic import AnyUrl, field_validator

from src.config.env import load_env
from src.primitives import FrozenBaseModel, NonEmptyStr


class TemporalConfig(FrozenBaseModel):
    """Connection details for the Temporal control plane (a Cloud namespace or a dev server).

    The endpoint is a URL carrying a scheme, host, and port (``grpc://localhost:7233`` for a
    plaintext dev server, ``grpcs://<namespace>.<account>.tmprl.cloud:7233`` for Temporal Cloud);
    the client derives the ``host:port`` target Temporal connects to. The scheme is required and the
    validator rejects any endpoint that does not resolve to a host and port — a bare ``host:port``
    parses its host as the URL scheme — so a missing scheme fails loudly rather than silently
    producing a broken target. Worker TLS / API-key auth is a separate deployment concern.
    """

    endpoint: AnyUrl
    namespace: NonEmptyStr

    @field_validator("endpoint")
    @classmethod
    def _require_host_and_port(cls, value: AnyUrl) -> AnyUrl:
        """Reject an endpoint without a host and port (e.g. a scheme-less ``host:port``)."""
        if value.host is None or value.port is None:
            raise ValueError(
                "endpoint must be a URL with a scheme, host, and port, e.g. grpc://localhost:7233"
            )
        return value

    @property
    def target(self) -> str:
        """The ``host:port`` target Temporal connects to."""
        return f"{self.endpoint.host}:{self.endpoint.port}"


@cache
def production_temporal_config() -> TemporalConfig:
    """Build the Temporal connection config from the environment, once per process."""
    load_env()
    return TemporalConfig(
        endpoint=AnyUrl(os.environ["TEMPORAL_ENDPOINT"]),
        namespace=os.environ["TEMPORAL_NAMESPACE"],
    )
