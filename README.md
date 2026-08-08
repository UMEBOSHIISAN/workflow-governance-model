# Workflow Governance Model

> A portable, fail-closed data model for governing AI-assisted workflows.

Workflow Governance Model (WGM) validates the evidence and authority trail
around a workflow. It includes a pure, non-executing candidate recommender;
it is not an agent runner, execution router, scheduler, credential manager,
or approval UI.

## What it models

```text
Evidence -> Claim -> Action proposal -> Human approval
  -> Execution receipt -> Verification
```

Each object has an immutable identifier and version. References are typed and
version-bound, so a stale or missing dependency is rejected instead of being
silently accepted.

## Safety properties

- A claim cannot be supported by weak evidence only.
- An action proposal declares a permission tier but cannot grant one.
- Approval is an auditable record, not execution authority.
- A completed workflow requires a verification object.
- A denied workflow can reopen only with explicitly declared new evidence.
- Validation has no network, filesystem mutation, process, or model side effect.

## Quick start

```sh
python3 -m unittest discover -s tests -v
```

```python
from wgm import validate_document

result = validate_document(document)
if not result.valid:
    for error in result.errors:
        print(error.code, error.path, error.message)
```

## Relationship to Mothership

Mothership is a portable local control plane. WGM is an optional governance
layer that validates workflow evidence and authority boundaries before a human
chooses any external action. Neither package installs, configures, or invokes
the other.

## Compose the public ecosystem

WGM can create or validate a portable reviewed-request handoff before
[Mothership Router](https://github.com/UMEBOSHIISAN/mothership-router) performs
its local, human-gated dry-run selection. [Mothership](https://github.com/UMEBOSHIISAN/mothership)
provides portable environment contracts and diagnostics around those tools.

The handoff is deliberately small and credential-free:

```json
{
  "schema_version": "1.0",
  "task_id": "review-20260808-001",
  "capability": "code-review",
  "risk": "low",
  "token_budget": 4000,
  "evidence_references": ["evidence:design-note-v1"]
}
```

See the [public handoff schema](schemas/workflow-handoff.schema.json),
[valid example](examples/handoff.valid.json), and the
[compatibility guide](docs/compatibility.md). This object never includes
credentials, prompts, outputs, local paths, or execution permission.

## Safe LLM routing

WGM can rank locally declared candidates with `recommend_route(task, registry)`.
The router considers a capability label, risk level, token budget, candidate
capacity, and a transparent `cost_rank`. It returns one recommendation and
its reasons; it never starts a process, uses credentials, retries, falls back,
or changes an approval state.

High-risk work always returns `human_review_required`. A user may connect the
result to a separate execution system only after reviewing the candidate,
credentials, egress, and exact command in that system.

Try the included examples:

```sh
PYTHONPATH=src python3 -m wgm examples/task.json examples/registry.json
```

The command only reads two JSON files and prints a recommendation. It does not
invoke a model or inspect a local machine.

## Non-goals

- Automatic model selection, retry, fallback, or execution.
- Credentials, endpoints, machine paths, host topology, or business policy.
- Replacing human approval with a model decision.

## Project docs

- [Architecture](docs/architecture.md)
- [Composition and compatibility](docs/compatibility.md)
- [Integration gates and roadmap](NEXT.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
