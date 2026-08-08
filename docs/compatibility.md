# Public composition and compatibility

WGM, Mothership Router, and Mothership are separate repositories. None
installs, discovers, or invokes another one automatically.

| Component | Current public version | Responsibility | Does not do |
| --- | --- | --- | --- |
| [Workflow Governance Model](https://github.com/UMEBOSHIISAN/workflow-governance-model) | 0.1.x | Validate workflow evidence and authority metadata; recommend candidates | Execute a command or grant authority |
| [Mothership Router](https://github.com/UMEBOSHIISAN/mothership-router) | 0.1.x | Check a local ready registry and a digest-bound human approval; emit a dry-run manifest | Load credentials or launch a provider |
| [Mothership](https://github.com/UMEBOSHIISAN/mothership) | 0.1.x | Portable environment contracts and diagnostics | Install or operate the other components |

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
