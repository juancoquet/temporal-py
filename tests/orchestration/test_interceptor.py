"""The activity interceptor's ``Panic`` seam: what is remapped, and what is left alone."""

from collections.abc import Callable
from typing import cast, override

import pytest
from temporalio.exceptions import ApplicationError
from temporalio.worker import ActivityInboundInterceptor, ExecuteActivityInput

from src.orchestration.interceptor import PanicInterceptor, _PanicMapping
from src.primitives import Panic, ReturnedError


class _Boom(Panic):
    """A concrete panic for the tests."""


class _ReturnedBoom(ReturnedError):
    """A concrete returned error for the tests."""


class _Leaf(ActivityInboundInterceptor):
    """A leaf interceptor with no real ``next``; stands in for the activity call itself."""

    def __init__(self, outcome: Callable[[], object]) -> None:
        super().__init__(cast("ActivityInboundInterceptor", self))
        self._outcome = outcome

    @override
    async def execute_activity(self, input: ExecuteActivityInput) -> object:
        return self._outcome()


def _mapping(outcome: Callable[[], object]) -> _PanicMapping:
    return _PanicMapping(_Leaf(outcome))


# execute_activity never inspects its input on these paths, so a placeholder suffices.
_INPUT = cast(ExecuteActivityInput, object())


@pytest.mark.small
async def test_raised_panic_becomes_non_retryable_application_error():
    def outcome() -> object:
        raise _Boom("boom")

    with pytest.raises(ApplicationError) as exc_info:
        _ = await _mapping(outcome).execute_activity(_INPUT)

    error = exc_info.value
    assert error.non_retryable is True
    assert error.type == "_Boom"
    assert isinstance(error.__cause__, _Boom)


@pytest.mark.small
async def test_returned_error_is_not_remapped():
    def outcome() -> object:
        return _ReturnedBoom("returned, not raised")

    result = await _mapping(outcome).execute_activity(_INPUT)
    assert isinstance(result, _ReturnedBoom)


@pytest.mark.small
async def test_transient_exception_propagates_untouched():
    def outcome() -> object:
        raise RuntimeError("transient")

    with pytest.raises(RuntimeError, match="transient"):
        _ = await _mapping(outcome).execute_activity(_INPUT)


@pytest.mark.small
def test_interceptor_installs_the_panic_mapping():
    installed = PanicInterceptor().intercept_activity(_Leaf(lambda: None))
    assert isinstance(installed, _PanicMapping)
