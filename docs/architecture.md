# Architecture

WGM has two deliberately separate functions:

1. `validate_document` checks a workflow's evidence and authority trail.
2. `recommend_route` ranks locally declared candidates without selecting an
   executor or performing any side effect.

```mermaid
flowchart LR
    task[Bounded task metadata] --> validate[Workflow validation]
    evidence[Versioned evidence] --> validate
    validate --> review[Human review]
    task --> recommend[Pure candidate recommender]
    registry[Local candidate registry] --> recommend
    recommend --> review
    review --> external[Separate execution system]
```

The final arrow is outside WGM. The package neither implements nor authorizes
that external action.
