Yes. I closed the **two independent HTML documents** and also a bundle containing both.

### 1. Scientific and exploratory research

**[Open — Assurance & Evolution in tare.tools: Scientific and Exploratory Research](sandbox:/mnt/data/tare_tools_assurance_evolution_scientific_research_2026-08-09.html)**

The document contains **33 numbered chapters + bibliography**, covering the full arc we built in this conversation:

- definition of the problem beyond “software testing”;
- raw request → claims → oracle → evidence;
- **underconstraint × overconstraint/test overfitting**;
- psychometrics and test validity;
- metrology, calibration, drift, and traceability;
- Assurance Cases / GSN;
- domains × disciplines × methods × evidence;
- OWASP ASVS/MASVS/SCSVS, WCAG/WCAG-EM, and composition of specialized knowledge;
- mutation testing, ACH, SWE-Mutation, and testing the tests themselves;
- harmful mutations × semantics-preserving perturbations;
- regression-test selection and its limits;
- hermeticity as a foundation for **deterministic evidence reuse**;
- Bazel/Pants and incremental computation;
- scheduling, dynamic queues, and time-to-trust;
- Value of Information and experimental design;
- GUI, UX, and human/agentic journeys;
- trajectory/structural testing of agents;
- epistemic independence and held-outs;
- GitHub/DevOps as longitudinal sensors;
- production as delayed OutcomeEvidence;
- target ↔ local tare ↔ ecosystem ↔ central tare;
- Community Lab;
- federated evaluation;
- conformance packs;
- distributed falsification;
- secure artifact/knowledge distribution;
- `ADOPT / ADAPT / INSPIRE` matrix;
- consolidated architecture;
- experimental program and falsifiable hypotheses;
- roadmap and anti-patterns.

The recent state of the art strongly reinforced several of our points. A July 2026 survey synthesizes **257 works** on validation of agentic systems and specifically identifies temporal validity, runtime evidence, and assurance of open multi-agent systems as gaps. ([arxiv.org](https://arxiv.org/abs/2607.29405)) At the same time, SWE-Mutation empirically shows that LLM-generated suites still have serious difficulty discriminating faulty implementations, while studies on test overfitting/reward hacking show that visible tests can become optimization targets instead of independent verification instruments. ([arxiv.org](https://arxiv.org/abs/2605.22175))

The connection we made with ACH also gained industrial support: Meta's system uses concern-oriented mutation-guided LLM test generation, instead of simply maximizing the number of mutants/tests. ([dl.acm.org](https://dl.acm.org/doi/10.1145/3696630.3728544))

And I found two particularly good ancestors for our community idea. **Rust Crater** measures regressions from compiler changes against real ecosystem crates, while **MedPerf** takes evaluation to local data and allows results to be shared without moving the raw data. The combination is almost exactly the “central challenge → local execution → normalized evidence” pattern we envisioned. ([rustc-dev-guide.rust-lang.org](https://rustc-dev-guide.rust-lang.org/tests/crater.html))

---

### 2. Technical proposal for harness analysis

**[Open — tare.tools Assurance & Evolution Plane: Technical Architecture and Contracts Proposal](sandbox:/mnt/data/tare_tools_assurance_evolution_implementation_proposal_2026-08-09.html)**

This one has **42 chapters + bibliography** and is deliberately marked:

> **PROPOSED TARGET — do not implement directly without reconciliation against canonical CURRENT.**

It turns the research into an implementable design, while avoiding premature ratification of primitives.

Among the main parts:

- bounded-context ownership;
- mandatory reuse of canonical primitives;
- explicit list of **provisional semantic/contract roles**, not new primitives;
- modeling of `KnowledgeSource → Domain → Discipline → NormalizedControl`;
- global → project → path/component → task/change layering;
- applicability;
- governed waivers;
- compilation of the raw request;
- claim classes;
- Assurance Compiler;
- oracle hierarchy;
- evidence quality;
- EvidenceFamily and independence;
- complete sufficiency states;
- deterministic Evidence Reuse;
- Impact Graph;
- `EvidenceWorkItem`;
- resource requirements;
- dynamic scheduler;
- retrofit of the Regression Treasury;
- scenario deflation;
- meta-assurance;
- adapters for evidence producers;
- GUI/user journeys;
- stochastic agent evaluation;
- Assurance Health;
- GitHub/GitLab/Azure DevOps adapters;
- Community Lab;
- community threat model;
- TUF/Sigstore/SLSA/in-toto/OCI;
- conformance × qualification;
- Evolution Control;
- global prior × local posterior;
- **11 Strangler slices**;
- parity/rollback invariants;
- **22 BDD scenarios** for future SPECs;
- possible ADR/SPEC candidates, without ratifying them;
- experimental program;
- Windows/POSIX/consumer-GPU requirements;
- security/privacy;
- Implementation Packet strategy.

The central architecture became:

```text id="jaczo7"
RAW INTENT / SPECS / PROJECT MODEL
                │
                ▼
          Claim Bindings
                │
      Applicability + Risk
                ▼
        Required Assurance
                │
         evidence valid?
        ┌───────┴────────┐
        ▼                ▼
      REUSE          stale/missing
        │                │
        │         Evidence Planning
        │                │
        └───────┬────────┘
                ▼
        Evidence DAG / WorkItems
                │
    resource-aware scheduling
                │
  tools ─ tests ─ agents ─ humans
                │
                ▼
         OutcomeEvidence
                │
         EvidenceFamily
                │
 validity / independence / freshness
                │
                ▼
      Sufficiency Decision
                │
              Gate
                │
            Authority
                │
        real-world outcomes
                │
                ▼
 Attribution / Reputation / Evolution
```

This decomposition is deliberately compatible with the principle of **not allowing an external technology to own our control plane**. For example, Bazel inspires CAS/invalidation, Pants dependency inference, Develocity predictive selection, Sonobuoy conformance packs, and TUF/Sigstore/SLSA/OCI secure distribution — but none of them needs to become the kernel's semantic foundation. Develocity currently selects relevant tests explicitly through a predictive model, while TUF addresses threats such as rollback/freeze/mix-and-match in update systems. ([docs.develocity.ai](https://docs.develocity.ai/2026.2/using-develocity/predictive-test-selection/))

### 3. Bundle

**[Download — Bundle with both HTML files](sandbox:/mnt/data/tare_tools_assurance_evolution_research_bundle_2026-08-09.zip)**

I structurally validated the files: **no duplicate IDs and no broken internal anchors**. Each contains **75 cataloged references**, with links in the body and a final bibliography.

SHA-256:

```text id="tv5k5f"
Research:
a080996d1866ca05ca769557af13fe9e2d8ccfe72c6368ea284bcbf871be291b

Technical proposal:
9fa4ba0d4c0ef36bf2ebcbe9f47605a5a1967f7114116adc43ab9781cd722ea4

Bundle:
bc7123720a80c0fb1b7991f87cbcb727dadf8300ea3d09d113bfcffb554ceb9e
```

One new finding I consider especially strong is that **WCAG-EM 2.0 was published on July 23, 2026** and explicitly expanded the accessibility evaluation methodology beyond websites to include apps and other digital products. It is a very current example of exactly the separation we proposed: **standard/control ≠ methodology ≠ evidence producer**. ([w3.org](https://www.w3.org/TR/wcag-em-2/))

The final thesis of the documents became somewhat more precise than “Assurance Plane”:

> **tare.tools can treat assurance as a scientific-operational system for acquiring and maintaining evidence: preserve relevant claims, measure the strength and validity of the instruments that verify them, acquire only marginally useful evidence, learn from real outcomes, and evolve both by adding missing constraints and removing fossilized constraints — while always keeping authority and promotion deterministic.**
