"""Pure, fail-closed validation for the public Workflow Governance Model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_STATE_ARTIFACTS = {
    "awaiting_approval": "Approval",
    "executed": "ExecutionReceipt",
    "verified": "Verification",
    "denied": "Denial",
}
_KINDS = {
    "Evidence",
    "Claim",
    "ActionProposal",
    "Approval",
    "ExecutionReceipt",
    "Verification",
    "Denial",
}


@dataclass(frozen=True)
class ValidationError:
    path: str
    code: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def add(self, path: str, code: str, message: str) -> None:
        self.errors.append(ValidationError(path, code, message))


def validate_document(document: object) -> ValidationResult:
    """Validate one portable workflow document without performing any action."""
    result = ValidationResult()
    if not isinstance(document, dict):
        result.add("$", "DOCUMENT_TYPE", "document must be an object")
        return result
    if document.get("schema_version") != "1.0":
        result.add("schema_version", "SCHEMA_VERSION", "schema_version must be '1.0'")
    state = document.get("state")
    if state not in {"discover", "proposed", "awaiting_approval", "approved", "executed", "verified", "denied"}:
        result.add("state", "STATE", "state is not a supported workflow state")
    objects = document.get("objects")
    if not isinstance(objects, list):
        result.add("objects", "OBJECTS_TYPE", "objects must be a list")
        return result
    index: dict[str, dict[str, Any]] = {}
    for number, item in enumerate(objects):
        path = f"objects[{number}]"
        if not isinstance(item, dict):
            result.add(path, "OBJECT_TYPE", "workflow object must be an object")
            continue
        identifier = item.get("id")
        kind = item.get("kind")
        version = item.get("version")
        if not isinstance(identifier, str) or not identifier:
            result.add(f"{path}.id", "ID", "id must be a non-empty string")
        elif identifier in index:
            result.add(f"{path}.id", "DUPLICATE_ID", "id must be unique")
        else:
            index[identifier] = item
        if kind not in _KINDS:
            result.add(f"{path}.kind", "KIND", "kind is not a supported workflow object")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            result.add(f"{path}.version", "VERSION", "version must be a positive integer")
    for number, item in enumerate(objects):
        if isinstance(item, dict):
            _validate_object(item, f"objects[{number}]", index, result)
    required = _STATE_ARTIFACTS.get(state)
    if required and not any(item.get("kind") == required for item in index.values()):
        result.add("state", "STATE_ARTIFACT", f"state '{state}' requires a {required} object")
    return result


def _validate_object(item: dict[str, Any], path: str, index: dict[str, dict[str, Any]], result: ValidationResult) -> None:
    references = item.get("references", [])
    if not isinstance(references, list):
        result.add(f"{path}.references", "REFERENCES_TYPE", "references must be a list")
    else:
        for number, reference in enumerate(references):
            reference_path = f"{path}.references[{number}]"
            if not isinstance(reference, dict):
                result.add(reference_path, "REFERENCE_TYPE", "reference must be an object")
                continue
            target = index.get(reference.get("id"))
            if target is None:
                result.add(reference_path, "REFERENCE_MISSING", "referenced object is absent")
                continue
            if reference.get("kind") != target.get("kind"):
                result.add(reference_path, "REFERENCE_KIND", "reference kind does not match target")
            if reference.get("version") != target.get("version"):
                result.add(reference_path, "REFERENCE_STALE", "reference version does not match target")
    if item.get("kind") == "Claim":
        _validate_claim(item, path, index, result)
    if item.get("kind") == "Approval":
        if item.get("decision") not in {"approved", "denied"}:
            result.add(f"{path}.decision", "APPROVAL_DECISION", "approval decision must be approved or denied")
        if not isinstance(item.get("approver"), str) or not item.get("approver"):
            result.add(f"{path}.approver", "APPROVER", "approval requires a non-empty human approver identifier")
    if item.get("kind") == "Denial" and item.get("reopen_policy") not in {"never", "new_evidence", "manual"}:
        result.add(f"{path}.reopen_policy", "REOPEN_POLICY", "denial requires an explicit reopen policy")


def _validate_claim(item: dict[str, Any], path: str, index: dict[str, dict[str, Any]], result: ValidationResult) -> None:
    evidence = [index.get(reference.get("id")) for reference in item.get("references", []) if isinstance(reference, dict)]
    if not evidence:
        result.add(path, "CLAIM_EVIDENCE", "claim requires at least one evidence reference")
        return
    strengths = {entry.get("strength") for entry in evidence if isinstance(entry, dict) and entry.get("kind") == "Evidence"}
    if not strengths:
        result.add(path, "CLAIM_EVIDENCE", "claim references must include evidence")
    elif strengths <= {"weak"}:
        result.add(path, "WEAK_ONLY_CLAIM", "claim cannot rely on weak evidence only")
