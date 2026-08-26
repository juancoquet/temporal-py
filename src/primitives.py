"""Shared primitive types, base models, and sentinels used across the codebase.

Imports nothing heavy and nothing from Temporal, so anything may depend on it.
"""

from typing import Annotated, ClassVar, Literal, TypeIs, override

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _reject_blank(value: str) -> str:
    """Reject strings with no non-whitespace content, so blank can never mean present."""
    if not value.strip():
        raise ValueError("must contain non-whitespace characters")
    return value


type NonEmptyStr = Annotated[str, Field(min_length=1), AfterValidator(_reject_blank)]


class FrozenBaseModel(BaseModel):
    """Base for immutable value models; subclasses inherit the frozen config."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)


class NotGiven:
    """Sentinel for arguments the caller did not supply, where ``None`` is a meaningful value."""

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()


def was_given[T](value: T | NotGiven) -> TypeIs[T]:
    """Narrow *value* to ``T`` when it is not the ``NOT_GIVEN`` sentinel."""
    return not isinstance(value, NotGiven)
