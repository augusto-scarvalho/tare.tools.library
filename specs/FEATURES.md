# Feature Specs

Use this folder for feature-level behavior, scenarios, edge cases, acceptance criteria, and validation expectations.

Feature specs should be specific enough for an agent to implement or test behavior without guessing product intent.

## Recommended structure

Each feature spec should include:

- goal and user/system outcome;
- in-scope and out-of-scope behavior;
- actors, preconditions, and trigger events;
- normal flow and important alternatives;
- edge cases and failure modes;
- acceptance criteria;
- relevant universal/project/architecture/stack specs;
- validation commands or manual evidence expectations;
- coverage/regression notes when behavior is added or changed.

## Agent guidance

- Link feature specs from task files.
- Do not use feature specs as vague wishlists; convert them into actionable behavior and acceptance criteria.
- If a feature changes public interfaces, data protection, permissions, dependencies, or operational behavior, link the corresponding universal baseline specs and escalate when needed.

## Greenfield use

Start with one feature spec per implemented capability. Keep it short, but include enough acceptance criteria and validation notes that the agent does not need to infer requirements from code alone.
