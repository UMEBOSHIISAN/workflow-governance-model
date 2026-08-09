# Changelog

## Unreleased

- Reject non-string handoff schema versions as validation errors instead of
  raising an exception on otherwise valid JSON input.
- Added a closed Mothership 0.2.0 owner manifest and synthetic
  `governance-handoff` 1.1 example with tests for schema drift, forbidden
  authority carriers, private paths, and false effect boundaries.
- Define every portable handoff identifier as an ASCII token: an alphanumeric
  first character followed only by alphanumerics, `.`, `_`, `:`, or `-`, with
  drive-relative `X:` prefixes rejected. Runtime and JSON Schema enforce the
  same true-end grammar.
- Preserve the released `governance-handoff` 1.0 acceptance set and publish
  the narrowed portable contract as 1.1 instead of changing 1.0 in place.

## 0.2.1 - 2026-08-08

- Fixed public CI to include the `src/` package directory while running the standard-library test suite.

## 0.2.0 - 2026-08-08

- Added a versioned, metadata-only public handoff schema with valid and invalid examples.
- Added pure handoff validation and interoperability documentation for Mothership Router and Mothership.
- Added standard-library CI for Python 3.12 and 3.13.

## 0.1.0 - 2026-08-08

- Initial clean-room public model for validating workflow evidence and authority trails.
- Added a pure candidate recommender with transparent capability, risk, token, and cost rules.
- Added no-execution CLI examples.

No provider integration, credential handling, automatic execution, retry, or fallback is included.
