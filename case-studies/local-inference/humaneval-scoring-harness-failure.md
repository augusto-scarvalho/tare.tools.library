# Local AI Lab — HumanEval Scoring Harness Failure

**Status:** EMPIRICAL NEGATIVE EVIDENCE.

A local benchmark initially made ThinkingCap appear catastrophically bad (0/60). Investigation found that the scoring harness/sample construction/cache behavior was wrong; after correction the same line measured about 93.3%, exceeding another candidate in that test.

## Why this case is preserved

The failure was not “model quality changed”. The **measurement instrument** was invalid. It therefore directly supports the Assurance/Metrology thesis: benchmark harness, cache, prompt/sample construction and scoring code are part of evidence identity.

## Consequences

- keep exact benchmark harness/version/config in qualification evidence;
- seed known-positive/negative controls where possible;
- investigate implausible cliffs before changing routing policy;
- avoid propagating a false benchmark into reputation/model-selection history;
- preserve corrections and old verdict provenance instead of silently overwriting them.
