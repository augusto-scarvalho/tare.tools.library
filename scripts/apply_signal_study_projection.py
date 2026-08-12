#!/usr/bin/env python3
"""Apply reading-projection enhancements to generated bridge-edition HTML.

Source HTML under bridge-editions/ remains byte-preserved. This script only
modifies files inside the generated _site tree after Jekyll has copied them.

Projection responsibilities:
- apply SIGNAL styling;
- resolve historical [Pxx] internal-corpus citations to the best surviving
  living/proposal/evidence/provenance destination in the current research site.

The resolver is intentionally a projection adapter. It does not rewrite the
historical citation text and it does not claim that a living successor is the
same artifact as the cited historical source.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import os
import re

SITE = Path("_site")
BRIDGES = SITE / "bridge-editions"
STYLESHEET = SITE / "assets" / "signal-study.css"
SIGNAL_MARKER = 'data-signal-projection="true"'
REF_MARKER = 'data-internal-ref-resolution='

# Ordered from most specific to most general. Each rule resolves a historical
# citation to a *reading destination*, not to a claim of source identity.
REFERENCE_RULES: tuple[tuple[str, str, str], ...] = (
    ("mxc-q1", "case-studies/validation/fsv-mxc-staged-candidate-enumeration.html", "evidence"),
    ("fsv validation", "case-studies/validation/fsv-mxc-staged-candidate-enumeration.html", "evidence"),
    ("humaneval", "case-studies/local-inference/humaneval-scoring-harness-failure.html", "evidence"),
    ("agent relay", "case-studies/evidence-exchange/agent-relay-q0.html", "evidence"),
    ("kimi", "case-studies/vendor-runtime/kimi-antigravity-capability-parity.html", "evidence"),
    ("antigravity", "case-studies/vendor-runtime/kimi-antigravity-capability-parity.html", "evidence"),
    ("semantic curation v1", "case-studies/research-repository/semantic-curation-v1-failure.html", "evidence"),
    ("agent operating system sdd", "proposals/agent-os-sdd-bdd.html", "proposal"),
    ("sdd + bdd", "proposals/agent-os-sdd-bdd.html", "proposal"),
    ("harness → agent operating system", "research/foundations/agent-os-foundations.html", "living"),
    ("agent operating system scientific architecture", "research/foundations/agent-os-foundations.html", "living"),
    ("agent os foundations", "research/foundations/agent-os-foundations.html", "living"),
    ("project admission", "research/project/project-admission-adoption.html", "living"),
    ("demand lineage", "research/work/demand-lineage-settlement.html", "living"),
    ("workflow as governed work", "research/work/workflow-governed-work.html", "living"),
    ("workflow governed work", "research/work/workflow-governed-work.html", "living"),
    ("reliability semantics", "research/work/reliability-effect-reconciliation.html", "living"),
    ("effect reconciliation", "research/work/reliability-effect-reconciliation.html", "living"),
    ("information survival", "research/work/information-survival-reconstructability.html", "living"),
    ("canonical lineage", "research/context/canonical-lineage-identity.html", "living"),
    ("context & memory", "research/context/context-memory-playbooks.html", "living"),
    ("context memory", "research/context/context-memory-playbooks.html", "living"),
    ("memory playbooks", "research/context/context-memory-playbooks.html", "living"),
    ("adaptive learning", "research/context/adaptive-learning-cross-project-evolution.html", "living"),
    ("governance assurance & audit", "research/governance/governance-assurance-audit-metrology.html", "living"),
    ("governance assurance", "research/governance/governance-assurance-audit-metrology.html", "living"),
    ("assurance & evolution", "research/governance/assurance-evolution-testing.html", "living"),
    ("assurance and evolution", "research/governance/assurance-evolution-testing.html", "living"),
    ("test engineering", "research/assurance/test-engineering-scenario-gates.html", "living"),
    ("scenario gates", "research/assurance/test-engineering-scenario-gates.html", "living"),
    ("interoperability, learning & evolution", "proposals/interoperability-learning-evolution.html", "proposal"),
    ("interoperability, learning and evolution", "proposals/interoperability-learning-evolution.html", "proposal"),
    ("runtime/vendors + tui/repl", "research/runtime/runtime-ownership-vendor-integration.html", "living"),
    ("runtime ownership", "research/runtime/runtime-ownership-vendor-integration.html", "living"),
    ("vendor cli", "research/runtime/vendor-cli-runtime-landscape.html", "living"),
    ("capability", "research/runtime/capability-sandbox-resources.html", "living"),
    ("sandbox", "research/runtime/capability-sandbox-resources.html", "living"),
    ("protocols", "research/runtime/protocols-interoperability.html", "living"),
    ("interoperability", "research/runtime/protocols-interoperability.html", "living"),
    ("routing", "research/routing/adaptive-routing-reputation.html", "living"),
    ("reputation", "research/routing/adaptive-routing-reputation.html", "living"),
    ("economics", "research/routing/economics-resources-observability.html", "living"),
    ("observability", "research/routing/economics-resources-observability.html", "living"),
    ("tui/repl", "research/experience/tui-repl-experience.html", "living"),
    ("experience / ux", "research/experience/tui-repl-experience.html", "living"),
    ("legacy system reconstruction", "research/experience/legacy-system-reconstruction.html", "living"),
    ("local model lab", "research/local-inference/local-model-lab-methodology.html", "living"),
    ("model landscape", "research/local-inference/model-landscape-finetunes.html", "living"),
    ("finetunes", "research/local-inference/model-landscape-finetunes.html", "living"),
    ("formal research program", "research/methodology/formal-research-program.html", "living"),
    ("cmrp", "research/methodology/cmrp-and-epistemic-independence.html", "living"),
    ("private github snapshot", "sources/PROVENANCE_INDEX.html", "provenance"),
    ("snapshot docs/research", "sources/PROVENANCE_INDEX.html", "provenance"),
)

INTERNAL_REF_RE = re.compile(
    r'(<div class="ref" id="P\d+">.*?<strong>\[P\d+\]</strong>\s*)([^<]+)',
    re.DOTALL,
)


def normalize_title(raw: str) -> str:
    return " ".join(unescape(raw).casefold().split())


def resolve_reference(title: str) -> tuple[str, str]:
    normalized = normalize_title(title)
    for needle, target, kind in REFERENCE_RULES:
        if needle.casefold() in normalized:
            return target, kind
    return "sources/PROVENANCE_INDEX.html", "provenance"


def relative_site_href(source: Path, target: str) -> str:
    target_path = SITE / target
    if not target_path.is_file():
        raise RuntimeError(f"internal-reference target missing from generated site: {target}")
    return os.path.relpath(target_path, source.parent).replace(os.sep, "/")


def resolve_internal_refs(text: str, path: Path) -> tuple[str, int, int]:
    total = len(re.findall(r'<div class="ref" id="P\d+">', text))
    if total == 0:
        return text, 0, 0

    resolved = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal resolved
        prefix, raw_title = match.groups()
        target, kind = resolve_reference(raw_title)
        href = relative_site_href(path, target)
        resolved += 1
        return (
            f'{prefix}<a class="internal-ref-link" '
            f'data-internal-ref-resolution="{kind}" href="{href}" '
            f'title="Open {kind} reading destination">{raw_title.strip()}</a>'
            f' <span class="internal-ref-kind">{kind}</span> '
        )

    if REF_MARKER not in text:
        text = INTERNAL_REF_RE.sub(repl, text)
    else:
        resolved = len(re.findall(REF_MARKER, text))

    if resolved != total:
        raise RuntimeError(
            f"internal-reference projection incomplete for {path}: "
            f"resolved {resolved}/{total}"
        )
    return text, resolved, total


def project(path: Path) -> tuple[bool, int, int]:
    text = path.read_text(encoding="utf-8")
    if "</head>" not in text or "<html" not in text:
        raise RuntimeError(f"unexpected HTML structure: {path}")

    themed = False
    if SIGNAL_MARKER not in text:
        rel_css = os.path.relpath(STYLESHEET, path.parent).replace(os.sep, "/")
        text = text.replace("<html", f'<html {SIGNAL_MARKER}', 1)
        text = text.replace("</head>", f'<link rel="stylesheet" href="{rel_css}"></head>', 1)
        themed = True

    text, resolved, total = resolve_internal_refs(text, path)
    path.write_text(text, encoding="utf-8")
    return themed, resolved, total


def main() -> None:
    if not STYLESHEET.is_file():
        raise SystemExit(f"missing projection stylesheet: {STYLESHEET}")
    if not BRIDGES.is_dir():
        raise SystemExit(f"missing generated bridge directory: {BRIDGES}")
    files = sorted(BRIDGES.rglob("*.html"))
    if not files:
        raise SystemExit("no generated bridge HTML files found")

    themed = resolved = references = 0
    for path in files:
        did_theme, file_resolved, file_total = project(path)
        themed += int(did_theme)
        resolved += file_resolved
        references += file_total

    print(f"SIGNAL study projection: {themed}/{len(files)} HTML files themed")
    print(f"Internal corpus references: {resolved}/{references} resolved")


if __name__ == "__main__":
    main()
