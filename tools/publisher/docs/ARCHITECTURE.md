# Publisher Architecture

```text
Publication Packet
      ↓
manifest/schema validation
      ↓
DOCUMENT_POLICY
      ↓
deterministic route
      ↓
filesystem/local-git backend (CURRENT bootstrap)
      ↓
GitHub backend (TARGET adapter)
```

The backend must never own policy. A GitHub App, Codex or another transport is replaceable infrastructure.
