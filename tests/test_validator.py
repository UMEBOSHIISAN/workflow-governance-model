from __future__ import annotations

import unittest
from unittest import mock
import json
from pathlib import Path

from wgm import validate_document, validate_handoff
from wgm.router import recommend_route
from wgm.__main__ import main


def evidence(identifier: str = "evidence-1", strength: str = "authoritative") -> dict[str, object]:
    return {"id": identifier, "kind": "Evidence", "version": 1, "strength": strength}


class WorkflowGovernanceTests(unittest.TestCase):
    def test_valid_claim_with_authoritative_evidence(self) -> None:
        document = {
            "schema_version": "1.0",
            "state": "proposed",
            "objects": [
                evidence(),
                {"id": "claim-1", "kind": "Claim", "version": 1, "references": [{"id": "evidence-1", "kind": "Evidence", "version": 1}]},
            ],
        }
        self.assertTrue(validate_document(document).valid)

    def test_weak_evidence_only_is_rejected(self) -> None:
        document = {
            "schema_version": "1.0",
            "state": "proposed",
            "objects": [
                evidence(strength="weak"),
                {"id": "claim-1", "kind": "Claim", "version": 1, "references": [{"id": "evidence-1", "kind": "Evidence", "version": 1}]},
            ],
        }
        self.assertIn("WEAK_ONLY_CLAIM", {error.code for error in validate_document(document).errors})

    def test_stale_reference_is_rejected(self) -> None:
        document = {
            "schema_version": "1.0",
            "state": "proposed",
            "objects": [
                evidence(),
                {"id": "claim-1", "kind": "Claim", "version": 1, "references": [{"id": "evidence-1", "kind": "Evidence", "version": 2}]},
            ],
        }
        self.assertIn("REFERENCE_STALE", {error.code for error in validate_document(document).errors})

    def test_verified_state_requires_verification(self) -> None:
        document = {"schema_version": "1.0", "state": "verified", "objects": []}
        self.assertIn("STATE_ARTIFACT", {error.code for error in validate_document(document).errors})


class RoutingTests(unittest.TestCase):
    def test_recommends_lowest_cost_eligible_candidate(self) -> None:
        task = {"capability": "analysis", "risk": "low", "tokens": 4000}
        registry = {
            "candidates": [
                {"alias": "local-fast", "capabilities": ["analysis"], "max_risk": "low", "max_tokens": 8000, "cost_rank": 1},
                {"alias": "cloud-careful", "capabilities": ["analysis"], "max_risk": "high", "max_tokens": 32000, "cost_rank": 2},
            ]
        }
        result = recommend_route(task, registry)
        self.assertEqual("local-fast", result["recommended_alias"])
        self.assertFalse(result["authority_effect"])
        self.assertFalse(result["execution_effect"])

    def test_high_risk_requires_human_review(self) -> None:
        task = {"capability": "analysis", "risk": "high", "tokens": 100}
        registry = {"candidates": [{"alias": "careful", "capabilities": ["analysis"], "max_risk": "high", "max_tokens": 1000, "cost_rank": 1}]}
        result = recommend_route(task, registry)
        self.assertIsNone(result["recommended_alias"])
        self.assertEqual("human_review_required", result["status"])

    def test_rejects_ineligible_candidates_without_fallback_execution(self) -> None:
        task = {"capability": "coding", "risk": "low", "tokens": 5000}
        registry = {"candidates": [{"alias": "small", "capabilities": ["coding"], "max_risk": "low", "max_tokens": 100, "cost_rank": 1}]}
        result = recommend_route(task, registry)
        self.assertIsNone(result["recommended_alias"])
        self.assertEqual("no_eligible_candidate", result["status"])

    def test_cli_requires_two_input_files(self) -> None:
        with mock.patch("sys.stderr") as stderr:
            self.assertEqual(2, main([]))
        self.assertTrue(stderr.write.called)


class HandoffTests(unittest.TestCase):
    def test_valid_public_handoff_is_accepted(self) -> None:
        example = json.loads((Path(__file__).parents[1] / "examples" / "handoff.valid.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_handoff(example))

    def test_handoff_rejects_execution_authority_and_unknown_fields(self) -> None:
        example = json.loads((Path(__file__).parents[1] / "examples" / "handoff.invalid.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_handoff(example))

    def test_handoff_rejects_empty_evidence_references(self) -> None:
        handoff = {"schema_version": "1.0", "task_id": "task-1", "capability": "analysis", "risk": "low", "token_budget": 1, "evidence_references": []}
        self.assertTrue(validate_handoff(handoff))


if __name__ == "__main__":
    unittest.main()
