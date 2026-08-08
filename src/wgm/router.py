"""Pure candidate recommendation; intentionally not an execution engine."""

from __future__ import annotations

from typing import Any


_RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def recommend_route(task: object, registry: object) -> dict[str, object]:
    """Return an inspectable routing recommendation with no authority effect.

    High-risk work is never automatically recommended.  This function neither
    launches a command nor mutates a registry; an operator must separately
    review any low- or medium-risk recommendation.
    """
    if not isinstance(task, dict) or not isinstance(registry, dict):
        return _result("invalid_input", None, ["task_and_registry_must_be_objects"])
    capability = task.get("capability")
    risk = task.get("risk")
    tokens = task.get("tokens")
    if not isinstance(capability, str) or risk not in _RISK_ORDER or not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 1:
        return _result("invalid_input", None, ["task_requires_capability_supported_risk_and_positive_tokens"])
    if risk == "high":
        return _result("human_review_required", None, ["high_risk_work_is_not_auto_routed"])
    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        return _result("invalid_input", None, ["registry_requires_candidate_list"])
    eligible: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if (
            isinstance(candidate.get("alias"), str)
            and isinstance(candidate.get("capabilities"), list)
            and capability in candidate["capabilities"]
            and candidate.get("max_risk") in _RISK_ORDER
            and _RISK_ORDER[candidate["max_risk"]] >= _RISK_ORDER[risk]
            and isinstance(candidate.get("max_tokens"), int)
            and not isinstance(candidate.get("max_tokens"), bool)
            and candidate["max_tokens"] >= tokens
            and isinstance(candidate.get("cost_rank"), int)
            and not isinstance(candidate.get("cost_rank"), bool)
        ):
            eligible.append(candidate)
    if not eligible:
        return _result("no_eligible_candidate", None, ["no_candidate_matches_capability_risk_and_token_budget"])
    chosen = min(eligible, key=lambda item: (item["cost_rank"], item["alias"]))
    return _result("recommended", chosen["alias"], ["eligible_candidate_with_lowest_cost_rank"])


def _result(status: str, alias: str | None, reasons: list[str]) -> dict[str, object]:
    return {
        "status": status,
        "recommended_alias": alias,
        "reasons": reasons,
        "authority_effect": False,
        "execution_effect": False,
    }
