# EXP-XXX: [Short experiment title]

- **Status:** [PROPOSED | RUNNING | ADOPTED | ADAPTED | RETIRED]
- **Run date:** YYYY-MM-DD
- **Executor:** [Operator or agent name]
- **Code commit / version:** `@ <hash-or-branch>`
- **Hardware / substrate:** e.g. operator-configured GPU (24 GB VRAM) / hosted API tier

---

## 1. Hypothesis and objective
* **Central question:** What are we trying to prove or falsify?
* **Null hypothesis ($H_0$):** What would happen without this change?
* **Alternative hypothesis ($H_1$):** The expected measurable gain.

---

## 2. Method and setup
* **Test scenario:** An objective description of the execution steps.
* **Commands run:**
  ```powershell
  # Example benchmark command
  python -m pytest tests/benchmarks/
  ```

---

## 3. Observed data and metrics

| Parameter / metric | Baseline (before) | New result | Delta (%) |
| :--- | :--- | :--- | :--- |
| **Mean latency ($p_{50}$)** | 250ms | 45ms | -82.0% |
| **Token consumption** | 12,000 tokens | 2,100 tokens | -82.5% |
| **Throughput (req/s)** | 4.2 req/s | 22.1 req/s | +426% |
| **Error / drift rate** | 0.0% | 0.0% | 0.0% |

---

## 4. Architectural verdict and next steps
* **Verdict:** `[ADOPT | ADAPT | RETIRE]`
* **Rationale:** Why was this decision taken, based on the numbers above?
* **Impact on ADRs:** Does it need a new ADR or an amendment?
