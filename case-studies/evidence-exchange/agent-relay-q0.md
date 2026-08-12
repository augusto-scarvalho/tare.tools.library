# Agent Relay Q0 — evidence exchange case study

**Status:** OPERATIONAL EXPERIMENT / security finding.

The auditor published backlog through a GitHub Issue; the implementer read it directly, stopped at OWNER_AUTH_REQUIRED when no authenticated Drive transport existed, and after owner bootstrap published a four-file evidence package to Google Drive with manifest and READY-last semantics. The auditor independently downloaded cloud bytes and verified hashes.

## Proven chain

ChatGPT auditor → GitHub Issue → implementer → Google Drive Desktop/cloud → auditor Drive connector → independent byte verification.

This removed manual ZIP transport from the owner loop.

## Security findings

The initial Drive setup exposed personal My Drive directory names to broad host listing. Filesystem confinement was **not proven**. Auditor/implementer/owner also used the same GitHub account, so protocol `senderRole` did not prove cryptographic role identity.

Local mount path was shown to be an observation, not evidence identity: bytes/hash/cloud locator are stronger.

## Architectural lesson

Git = subject/candidate; Issue = coordination envelope; Drive = bulky temporary evidence backend; Actions = CI evidence; chat = owner notification. Drive is a backend, never an Evidence Plane/Authority primitive.
