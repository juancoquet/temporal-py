"""The orchestration data converter preserves unrelated application failures."""

import pytest
from temporalio.api.failure.v1 import Failure
from temporalio.exceptions import ApplicationError

from src.orchestration.converter import orchestration_data_converter


@pytest.mark.small
def test_validation_error_type_alone_does_not_make_an_outer_failure_non_retryable():
    inner = ApplicationError("Inner failure", type="ValidationError", non_retryable=True)
    outer = ApplicationError("Outer failure", type="DomainFailure")
    outer.__cause__ = inner
    failure = Failure()

    orchestration_data_converter.failure_converter.to_failure(
        outer,
        orchestration_data_converter.payload_converter,
        failure,
    )

    assert failure.application_failure_info.type == "DomainFailure"
    assert not failure.application_failure_info.non_retryable
