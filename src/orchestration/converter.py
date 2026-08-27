"""Temporal payload conversion with terminal failures for malformed typed payloads."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from pydantic import ValidationError
from temporalio.contrib.pydantic import PydanticPayloadConverter
from temporalio.converter import DataConverter, DefaultFailureConverter, PayloadConverter
from temporalio.exceptions import ApplicationError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from temporalio.api.common.v1 import Payload
    from temporalio.api.failure.v1 import Failure

_VALIDATION_ERROR_TYPE = "ValidationError"


class _NonRetryableValidationError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            "Payload validation failed",
            type=_VALIDATION_ERROR_TYPE,
            non_retryable=True,
        )


class _NonRetryableValidationPayloadConverter(PydanticPayloadConverter):
    @override
    def from_payloads(
        self,
        payloads: Sequence[Payload],
        type_hints: list[type] | None = None,
    ) -> list[object]:
        try:
            return super().from_payloads(payloads, type_hints)
        except ValidationError as error:
            raise _NonRetryableValidationError from error


class _NonRetryableValidationFailureConverter(DefaultFailureConverter):
    @override
    def to_failure(
        self,
        exception: BaseException,
        payload_converter: PayloadConverter,
        failure: Failure,
    ) -> None:
        # The activity worker wraps argument-decoding failures in another ApplicationError. Recover
        # the non-retryable error produced by our payload converter before serialising the failure.
        validation_error = (
            _find_non_retryable_validation_error(exception)
            if isinstance(exception, ApplicationError)
            else None
        )
        failure_exception = validation_error if validation_error is not None else exception
        super().to_failure(failure_exception, payload_converter, failure)


def _find_non_retryable_validation_error(
    exception: BaseException,
) -> _NonRetryableValidationError | None:
    current: BaseException | None = exception
    while current is not None:
        if isinstance(current, _NonRetryableValidationError):
            return current
        current = current.__cause__
    return None


orchestration_data_converter = DataConverter(
    payload_converter_class=_NonRetryableValidationPayloadConverter,
    failure_converter_class=_NonRetryableValidationFailureConverter,
)
