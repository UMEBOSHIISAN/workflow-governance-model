# Mothership suite compatibility

Workflow Governance Model owns the `governance-handoff` 1.1 semantics. The owner schema is
`schemas/workflow-handoff.1.1.schema.json`; Mothership 0.2.0 freezes those exact reviewed bytes for suite composition while
WGM remains independently installable.

The previously released `schemas/workflow-handoff.schema.json` remains the
permissive 1.0 contract. It is not silently narrowed; new suite integrations
select 1.1 explicitly.

The closed `suite/mothership-0.2-conformance.json` manifest binds the owner schema digest and
`examples/handoff.valid.json`. Reproduce it with:

```sh
PYTHONPATH=src python3 -m unittest tests.test_mothership_conformance -v
```

The handoff contains reviewed metadata only: a task identifier, capability, risk, bounded token budget, and opaque
evidence identifiers. It rejects execution permission, approval flags, commands, prompts, model output, credentials,
private paths, and all other unknown fields.

Mothership Router may consume this explicit metadata after review. Schema validity does not transfer approval or
execution authority, and neither repository discovers, installs, or invokes the other. See the
[Mothership protocol reference](https://github.com/UMEBOSHIISAN/mothership/blob/main/docs/protocols.md).

This is local conformance evidence, not a publication, production-accuracy, execution, or downstream-freshness claim.
