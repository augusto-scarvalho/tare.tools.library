# Private GitHub main snapshot — 2026-08-05

Status: **HISTORICAL BASELINE — NOT CURRENT**

This directory pins the exact content identity of the user-supplied private GitHub branch archive
`universal-agent-harness-prototype-main.zip`.

## What is proven

- Exact archive SHA-256: `2f4b2d9fa68b1a93b009ef0eb389a699f409568f74102b051bb03d06508b9a1e`
- Archive file count: **1242**
- Content tree SHA-256: `c20797d62bdc1135152dedf1750ecc2fcdb266b3ce884b70a50f5a359b5a85c3`
- Project metadata: `universal-agent-harness` version `0.9.0`
- The ZIP does not contain `.git`, therefore the remote Git commit SHA is **not proven**.
- All archive entries carry the same ZIP timestamp `2026-08-05T02:30:36`. This is recorded as archive metadata only.

## Authority

The owner reports that the live tare.tools checkout is newer and dirty. Therefore this snapshot is
historical reference evidence only. It must not be described as CURRENT.

## Negative evidence preserved

The snapshot contains release-integrity artifacts, but `python scripts/release_integrity.py verify`
fails for this exact tree. See `RELEASE_INTEGRITY_VERIFICATION.json`.

That failure means the embedded release bundle is stale/non-matching. It does **not** erase the value
of the ZIP as an exact historical content snapshot.

## Files

- `BASELINE.json` — machine-readable baseline metadata.
- `TREE_SHA256SUMS.txt` — exact per-file content identities.
- `RELEASE_INTEGRITY_VERIFICATION.json` — preserved verification failure.
- Source archive: `../../../corpus/source-bundles/universal-agent-harness-prototype-main-2026-08-05.zip`
