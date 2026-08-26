"""The activity interceptor that applies the ``Panic`` failure seam once, for every activity."""

from typing import Any, override

from temporalio.exceptions import ApplicationError
from temporalio.worker import (
    ActivityInboundInterceptor,
    ExecuteActivityInput,
    Interceptor,
)

from src.primitives import Panic


class _PanicMapping(ActivityInboundInterceptor):
    # Temporal types this hook's return as Any; we pass the activity result straight through
    # (only Panic is mapped), so the explicit Any and the ignores below are deliberate.
    @override
    async def execute_activity(  # pyright: ignore[reportAny]
        self, input: ExecuteActivityInput
    ) -> Any:  # pyright: ignore[reportExplicitAny]
        try:
            return await self.next.execute_activity(input)  # pyright: ignore[reportAny]
        except Panic as exc:
            raise ApplicationError(str(exc), type=type(exc).__name__, non_retryable=True) from exc


class PanicInterceptor(Interceptor):
    """Maps a raised :class:`~src.primitives.Panic` to a non-retryable Temporal failure.

    Installed on every activity worker, so a task raises the pure-domain ``Panic`` and stays
    Temporal-agnostic. Everything else is left alone: a transient error propagates untouched for
    Temporal to retry, and a returned error flows back as a value.
    """

    @override
    def intercept_activity(self, next: ActivityInboundInterceptor) -> ActivityInboundInterceptor:
        return _PanicMapping(next)
