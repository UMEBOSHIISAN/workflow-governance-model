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
    return (
        isinstance(value, str)
        and bool(value)
        and not any(
            character in "/\\"
            or ord(character) < 0x20
            or ord(character) == 0x7F
            for character in value
        )
    )


def validate_handoff(handoff: object) -> list[HandoffError]:
    """Validate metadata passed between public components without I/O or side effects."""
    if not isinstance(handoff, dict):
        return [HandoffError("$", "handoff must be an object")]
    errors: list[HandoffError] = []
    unexpected = set(handoff) - _ALLOWED_KEYS
    if unexpected:
        errors.append(HandoffError("$", "handoff contains unsupported fields"))
    if handoff.get("schema_version") != "1.0":
        errors.append(HandoffError("schema_version", "schema_version must be '1.0'"))
    for name in ("task_id", "capability"):
        if not _is_safe_identifier(handoff.get(name)):
            errors.append(HandoffError(name, f"{name} must be a non-path identifier"))
    if handoff.get("risk") not in _RISKS:
        errors.append(HandoffError("risk", "risk must be low, medium, or high"))
    budget = handoff.get("token_budget")
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        errors.append(HandoffError("token_budget", "token_budget must be a positive integer"))
    references = handoff.get("evidence_references")
    if not isinstance(references, list) or not references or any(not _is_safe_identifier(value) for value in references):
        errors.append(HandoffError("evidence_references", "evidence_references must be a non-empty list of non-path identifiers"))
    return errors
