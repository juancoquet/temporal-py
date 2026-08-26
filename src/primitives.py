"""Shared primitive types, base models, and sentinels used across the codebase.

This module imports nothing heavy and nothing from Temporal, so anything may depend on it —
including task/domain code that must stay runtime-agnostic (it raises :class:`Panic` from here
without ever importing ``temporalio``).
"""

import sys
from typing import Annotated, ClassVar, Literal, Self, TypeIs, override

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, RootModel, model_validator


def _reject_blank(value: str) -> str:
    """Reject strings with no non-whitespace content, so blank can never mean present."""
    if not value.strip():
        raise ValueError("must contain non-whitespace characters")
    return value


# ``min_length=1`` stays alongside the validator for the JSON-schema metadata it carries; the
# validator is the real gate.
type NonEmptyStr = Annotated[str, Field(min_length=1), AfterValidator(_reject_blank)]


class FrozenBaseModel(BaseModel):
    """Base for immutable value models; subclasses inherit the frozen config."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)


# The two error roots of the failure model. A domain outcome a caller is expected to observe and
# react to is *returned* as a ``ReturnedError`` value (typically as one arm of a result union); a
# failure no caller in the chain can recover from is *raised* as a ``Panic``. The orchestration
# activity interceptor maps a raised ``Panic`` onto a non-retryable Temporal failure, so task code
# stays Temporal-agnostic — it just raises ``Panic``.


class Panic(Exception):  # noqa: N818  # a raised failure category, named like ``ReturnedError``
    """Base for unrecoverable failures that are *raised*, never returned.

    Pure-domain, with no dependency on the execution layer. The name states the failure category
    rather than carrying an ``Error`` suffix, mirroring that it is raised, not returned.
    """


class ReturnedError(Exception):
    """Base for returned errors that remember the exception they came from.

    Constructing one while another exception is being handled records that active exception as this
    error's ``__cause__``, so a returned error still carries the original traceback when later
    re-raised — no manual ``__cause__`` wiring at the call site.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        current = sys.exc_info()[1]
        if current is not None:
            self.__cause__ = current


class Id(RootModel[str]):
    """Base for human-identifiable ids of the form ``<prefix>-<identifier>``.

    Each concrete id declares its prefix in the class header
    (``class WorkflowId(Id, prefix="wf")``). The keyword is required, so an id type without a prefix
    does not type-check. An id is a value object wrapping a single string: it prints and serialises
    as its plain string, while staying a nominally distinct type.
    """

    prefix: ClassVar[NonEmptyStr]

    def __init_subclass__(cls, *, prefix: NonEmptyStr) -> None:
        """Bake the required *prefix* into the subclass."""
        super().__init_subclass__()
        cls.prefix = prefix

    @model_validator(mode="after")
    def _validate_prefix(self) -> Self:
        """Reject any value that does not carry this type's prefix and an identifier."""
        if not self.root.startswith(f"{self.prefix}-") or len(self.root) <= len(self.prefix) + 1:
            raise ValueError(f"{type(self).__name__} must be '{self.prefix}-<identifier>'")
        return self

    @property
    def identifier(self) -> str:
        """The part after the prefix."""
        return self.root[len(self.prefix) + 1 :]

    @classmethod
    def from_identifier(cls, identifier: NonEmptyStr) -> Self:
        """Build an id of this type from its identifier, prepending the prefix."""
        return cls(f"{cls.prefix}-{identifier}")

    @override
    def __str__(self) -> str:
        return self.root

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.root!r})"


class NotGiven:
    """Sentinel type for arguments the caller did not supply.

    Use ``NOT_GIVEN`` as the default for optional parameters where ``None`` is (or could become) a
    meaningful value in its own right, so "nothing was passed" and "explicitly None" stay distinct.
    """

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()


def was_given[T](value: T | NotGiven) -> TypeIs[T]:
    """Narrow *value* to ``T`` when it is not the ``NOT_GIVEN`` sentinel."""
    return not isinstance(value, NotGiven)
