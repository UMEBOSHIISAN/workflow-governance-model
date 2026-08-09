"""Validation for the portable, credential-free public handoff contract."""

from __future__ import annotations

from dataclasses import dataclass


_RISKS = {"low", "medium", "high"}
_ALLOWED_KEYS = {"schema_version", "task_id", "capability", "risk", "token_budget", "evidence_references"}


@dataclass(frozen=True)
class HandoffError:
    path: str
    message: str


def _is_safe_identifier(value: object) -> bool:
    if not isinstance(value, str) or not value or not value.isascii():
        return False
    if not value[0].isalnum():
        return False
    if len(value) >= 2 and value[0].isalpha() and value[1] == ":":
        return False
    return all(character.isalnum() or character in "._:-" for character in value[1:])


def _is_legacy_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def validate_handoff(handoff: object) -> list[HandoffError]:
    """Validate metadata passed between public components without I/O or side effects."""
    if not isinstance(handoff, dict):
        return [HandoffError("$", "handoff must be an object")]
    errors: list[HandoffError] = []
    unexpected = set(handoff) - _ALLOWED_KEYS
    if unexpected:
        errors.append(HandoffError("$", "handoff contains unsupported fields"))
    version = handoff.get("schema_version")
    if not isinstance(version, str) or version not in {"1.0", "1.1"}:
        errors.append(HandoffError("schema_version", "schema_version must be '1.0' or '1.1'"))
    identifier_is_valid = _is_legacy_identifier if version == "1.0" else _is_safe_identifier
    for name in ("task_id", "capability"):
        if not identifier_is_valid(handoff.get(name)):
            message = "must be a non-empty string" if version == "1.0" else "must be a portable ASCII identifier"
            errors.append(HandoffError(name, f"{name} {message}"))
    if handoff.get("risk") not in _RISKS:
        errors.append(HandoffError("risk", "risk must be low, medium, or high"))
    budget = handoff.get("token_budget")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        errors.append(HandoffError("token_budget", "token_budget must be a positive integer"))
    references = handoff.get("evidence_references")
    if not isinstance(references, list) or not references or any(not identifier_is_valid(value) for value in references):
        kind = "identifiers" if version == "1.0" else "portable ASCII identifiers"
        errors.append(HandoffError("evidence_references", f"evidence_references must be a non-empty list of {kind}"))
    return errors
