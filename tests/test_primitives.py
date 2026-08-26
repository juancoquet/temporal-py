import pytest
from pydantic import ValidationError

from src.orchestration.contracts import WorkflowId
from src.primitives import Panic, ReturnedError


@pytest.mark.small
def test_panic_is_a_distinct_root_not_a_returned_error():
    # The two error roots are peers, never conflated by an except/isinstance on the wrong one.
    assert issubclass(Panic, Exception)
    assert not issubclass(Panic, ReturnedError)
    assert not issubclass(ReturnedError, Panic)


@pytest.mark.small
def test_returned_error_captures_the_active_exception_as_cause():
    original = ValueError("boom")
    try:
        raise original
    except ValueError:
        error = ReturnedError("translated")
    assert error.__cause__ is original


@pytest.mark.small
def test_id_round_trips_through_its_prefix():
    wid = WorkflowId.from_identifier("doc-1")
    assert str(wid) == "wf-doc-1"
    assert wid.identifier == "doc-1"


@pytest.mark.small
def test_id_rejects_a_value_without_its_prefix():
    with pytest.raises(ValidationError):
        WorkflowId("doc-1")
