# Publisher embedding

The document publisher is embedded in `tare.tools.research` because it is repository-local ingestion/publication tooling, not a separate tare.tools bounded context.

The earlier standalone `tare-tools-publisher` bootstrap repository is retained only in historical checkpoints/bundles. The intended v0.13 topology is two repositories:

1. `tare-tools` — canonical product/architecture repository.
2. `tare.tools.research` — private companion research/evidence repository, including its publisher tooling.

Promotion into canonical tare-tools remains a separate governed change; embedding the publisher does not grant research architectural authority.
