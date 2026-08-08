# Public composition and compatibility

WGM, Mothership Router, and Mothership are separate repositories. None
installs, discovers, or invokes another one automatically.

| Component | Current public version | Responsibility | Does not do |
| --- | --- | --- | --- |
| [Workflow Governance Model](https://github.com/UMEBOSHIISAN/workflow-governance-model) | 0.2.1 | Validate workflow evidence and authority metadata; recommend candidates | Execute a command or grant authority |
| [Mothership Router](https://github.com/UMEBOSHIISAN/mothership-router) | 0.2.0 | Check a local ready registry and a digest-bound human approval; emit a dry-run manifest | Load credentials or launch a provider |
| [Mothership](https://github.com/UMEBOSHIISAN/mothership) | 0.1.2 | Portable environment contracts and diagnostics | Install or operate the other components |

## Handoff contract

[`schemas/workflow-handoff.schema.json`](../schemas/workflow-handoff.schema.json)
is the public metadata shape for a reviewed request. It contains only a task
identifier, capability, risk, token budget, and opaque evidence references.
It must never carry credentials, prompts, model output, private paths, or
execution permission.

```text
Agent Frontdoor / local form
  -> WGM validates workflow evidence
  -> public handoff JSON (metadata only)
  -> Mothership Router emits a dry-run candidate manifest
  -> human manually reviews any separate local execution system
```

High-risk work stops for human review at both WGM routing and Router. A valid
handoff is neither approval nor execution authority.

## Mothership 0.2.0 candidate conformance

WGM owns `governance-handoff` 1.0. The local, unpublished Mothership 0.2.0
candidate freezes the exact owner schema bytes and validates the synthetic
`demo-review-001` handoff. The closed owner manifest and reproduction command
are in [`mothership-suite.md`](mothership-suite.md).

Router receives reviewed metadata, not approval or execution authority.
Conformance is shape/version/safety compatibility only; it does not claim that
either local commit is remotely reachable or released.
