# Identity Crosswalk

This directory stores one immutable-to-materialized mapping per File Library ID after exact source bytes have been acquired and verified.

A crosswalk does **not** rewrite the original discovery reference. It records:

- File Library ID and reference ID;
- exact local source path and SHA-256;
- materialization basis;
- reported historical SHA verification when available;
- resolved document ID;
- source language and translation readiness.

An empty collection is valid. This README intentionally keeps the directory present in ZIP/Git checkpoints so restored navigation has the same structure as the live tree.
