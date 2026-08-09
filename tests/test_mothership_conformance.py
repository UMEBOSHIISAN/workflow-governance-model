from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import unittest

from wgm import validate_handoff


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "suite/mothership-0.2-conformance.json"
SCHEMA = ROOT / "schemas/workflow-handoff.1.1.schema.json"
LEGACY_SCHEMA = ROOT / "schemas/workflow-handoff.schema.json"
EXAMPLE = ROOT / "examples/handoff.valid.json"
EXPECTED_KEYS = {
    "schema_version",
    "suite_release",
    "repository",
    "protocol_kind",
    "protocol_version",
    "schema_path",
    "schema_sha256",
    "example_path",
    "authority_effect",
    "execution_effect",
}


def _check_manifest(document: object) -> None:
    if type(document) is not dict or set(document) != EXPECTED_KEYS:
        raise ValueError("manifest shape")
    expected = {
        "schema_version": "mothership.conformance.v1",
        "suite_release": "0.2.0",
        "repository": "workflow-governance-model",
        "protocol_kind": "governance-handoff",
        "protocol_version": "1.1",
        "schema_path": "schemas/workflow-handoff.1.1.schema.json",
        "example_path": "examples/handoff.valid.json",
        "authority_effect": False,
        "execution_effect": False,
    }
    for name, value in expected.items():
        if document[name] != value or type(document[name]) is not type(value):
            raise ValueError(name)
    for name in ("schema_path", "example_path"):
        value = document[name]
        if type(value) is not str:
            raise ValueError(name)
        parsed = PurePosixPath(value)
        if (
            parsed.is_absolute()
            or parsed.as_posix() != value
            or any(part in ("", ".", "..") for part in parsed.parts)
            or not (ROOT / value).is_file()
        ):
            raise ValueError(name)
    if document["schema_sha256"] != hashlib.sha256(SCHEMA.read_bytes()).hexdigest():
        raise ValueError("schema_sha256")


class MothershipConformanceTests(unittest.TestCase):
    def test_closed_manifest_binds_owner_schema_and_example(self) -> None:
        _check_manifest(json.loads(MANIFEST.read_text("utf-8")))

    def test_manifest_rejects_drift_missing_files_and_effects(self) -> None:
        manifest = json.loads(MANIFEST.read_text("utf-8"))
        corruptions = {
            "extra": ("extra", "x"),
            "repository": ("repository", "mothership"),
            "kind": ("protocol_kind", "router-manifest"),
            "version": ("protocol_version", "2.0"),
            "path": ("schema_path", "../workflow-handoff.schema.json"),
            "missing": ("example_path", "examples/missing.json"),
            "digest": ("schema_sha256", "0" * 64),
            "authority": ("authority_effect", True),
            "authority_number": ("authority_effect", 0),
            "execution": ("execution_effect", True),
            "execution_number": ("execution_effect", 0),
        }
        for name, (field, value) in corruptions.items():
            with self.subTest(name=name):
                changed = copy.deepcopy(manifest)
                changed[field] = value
                with self.assertRaises(ValueError):
                    _check_manifest(changed)

    def test_golden_handoff_passes_the_production_validator(self) -> None:
        handoff = json.loads(EXAMPLE.read_text("utf-8"))
        self.assertEqual([], validate_handoff(handoff))
        self.assertEqual("1.1", handoff["schema_version"])
        self.assertEqual("demo-review-001", handoff["task_id"])
        self.assertEqual("code-review", handoff["capability"])
        self.assertEqual("low", handoff["risk"])
        self.assertGreater(handoff["token_budget"], 0)
        self.assertTrue(all("/" not in item for item in handoff["evidence_references"]))

    def test_owner_schema_uses_the_portable_true_end_token_grammar(self) -> None:
        schema = json.loads(SCHEMA.read_text("utf-8"))
        pattern = r"^(?![A-Za-z]:)[A-Za-z0-9][A-Za-z0-9._:-]*(?![\s\S])"
        self.assertEqual(pattern, schema["properties"]["task_id"]["pattern"])
        self.assertEqual(pattern, schema["properties"]["capability"]["pattern"])
        self.assertEqual(
            pattern,
            schema["properties"]["evidence_references"]["items"]["pattern"],
        )

    def test_released_1_0_identifier_acceptance_is_preserved(self) -> None:
        handoff = json.loads(EXAMPLE.read_text("utf-8"))
        handoff.update(
            schema_version="1.0",
            task_id="review #42",
            capability="日本語 review",
            evidence_references=["evidence #1"],
        )
        self.assertEqual([], validate_handoff(handoff))
        schema = json.loads(LEGACY_SCHEMA.read_text("utf-8"))
        self.assertEqual("1.0", schema["properties"]["schema_version"]["const"])
        for field in ("task_id", "capability"):
            self.assertNotIn("pattern", schema["properties"][field])
        self.assertNotIn("pattern", schema["properties"]["evidence_references"]["items"])

    def test_authority_carriers_and_private_paths_are_rejected(self) -> None:
        handoff = json.loads(EXAMPLE.read_text("utf-8"))
        forbidden = {
            "execution_permission": True,
            "approved": True,
            "command": ["run"],
            "prompt": "hidden",
            "model_output": "hidden",
            "credential": "hidden",
            "private_path": "/private/example",
        }
        for field, value in forbidden.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(handoff)
                changed[field] = value
                self.assertTrue(validate_handoff(changed))

        for private_value in (
            "/Users/example/private.json",
            "~/private.json",
            r"C:\\Users\\example\\private.json",
            r"\\server\share\private.json",
            r"\\?\C:\private.json",
            r"~\private.json",
            "../private.json",
            "private/path.json",
            "private\nvalue",
            "private\n",
            "private\x7fvalue",
            "private\x85value",
            "private\x9bvalue",
            "private\u2028value",
            "C:private.json",
            "日本語",
        ):
            for field in ("task_id", "capability"):
                with self.subTest(field=field, private_value=private_value):
                    changed = copy.deepcopy(handoff)
                    changed[field] = private_value
                    self.assertTrue(validate_handoff(changed))
            with self.subTest(field="evidence_references", private_value=private_value):
                changed = copy.deepcopy(handoff)
                changed["evidence_references"] = [private_value]
                self.assertTrue(validate_handoff(changed))


if __name__ == "__main__":
    unittest.main()
