# Next integration gates

This file records the work needed to make the public ecosystem complete
without merging independent repositories into an unsafe all-in-one system.

## Current topology

```text
Agent Frontdoor (bounded task input)
        |
        v
Workflow Governance Model (evidence + authority validation)
        |
        v
WGM pure recommender (candidate ranking only)
        |
        v
Mothership Router (separate, human-gated execution package)
        |
        v
Secretary TUI (read-only observation)
```

Every arrow is a reviewed handoff, not an automatic network call or implicit
authority grant.

## P0 — completed in 0.1.1

1. **Public document schema**
   - Define one versioned JSON Schema for the portable document shape.
   - Keep generic names only: no workstation paths, business terms, provider
     endpoints, or organization-specific role names.
   - Add valid and invalid example documents plus schema tests.

2. **Release hygiene**
   - Add a changelog, contribution guide, security policy, checksum manifest,
     and a clean-checkout test command.
   - Add CI that runs the standard-library test suite on supported Python.

3. **Composition contract**
   - Publish an explicit JSON handoff shape between Agent Frontdoor, WGM, and
     Mothership Router.
   - The contract carries only task identity, risk, capability, budget, and
     evidence references. It must never carry credentials, prompts, outputs,
     private paths, or execution permission.

## P1 — complete baseline for Mothership Router 0.1.0

1. **Clean-room extraction of the portable runtime**
   - Re-author the useful `portable/` behavior from the private transfer kit.
   - Exclude historical reference snapshots, private-transfer notices,
     provenance indexes, host-specific configuration, and any legacy secret
     loading behavior.

2. **Execution-gate contract**
   - Require a reviewed candidate alias, explicit human approval, exact command
     digest, bounded artifact root, and manual execute switch.
   - Preserve no retry, no fallback, no recursive invocation, and no
     background runner defaults.

3. **Provider adapter policy**
   - Keep provider adapters optional and locally configured.
   - A provider's credentials and endpoint setup must remain outside Git and
     outside the public package.

## P2 — ecosystem polish

1. Add read-only WGM result rendering to Secretary TUI through a documented,
   local-file-only adapter contract.
2. Add examples showing Agent Frontdoor task cards flowing through WGM before a
   human uses Mothership Router.
3. Add an interoperability matrix covering version compatibility and explicit
   non-dependencies among public repositories.

## Explicitly excluded

- Automatic execution, automatic fallback, retries, provider credentials, or
  background workers.
- Private governance OS files, logs, host topology, business operations,
  deployment systems, schedulers, and brand assets.
