# Mini User Study — Buggy Bell State Detection (N=5)

## Purpose

Assess whether the QuantumAI tool helps users spot silent bugs in quantum circuits faster and with greater confidence compared to unassisted inspection.

---

## Participant Instructions

You will be shown a Qiskit circuit. Your task is to:

1. Read the code carefully.
2. Decide whether you think the circuit contains a bug.
3. Note how long it took you to reach a decision (use a stopwatch or estimate in seconds).
4. Rate your confidence from 1 to 5 (1 = guessing, 5 = certain).

**Do not search the internet or consult external resources.**
Half of participants will use the QuantumAI tool; half will not — follow the experimenter's instructions.

---

## Circuit Under Test

Inspect the following code. It is intended to produce a Bell state (maximally entangled two-qubit state). Decide: does it contain a bug?

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(1, 0)   # CNOT: control=qubit 1, target=qubit 0
qc.measure([0, 1], [0, 1])
```

*No hints are provided. Record your answer, time, and confidence.*

---

## Results Table Template

| participant_id | used_tool | spotted_bug | time_seconds | confidence_1_to_5 |
|----------------|-----------|-------------|--------------|-------------------|
| P1             | no        |             |              |                   |
| P2             | no        |             |              |                   |
| P3             | yes       |             |              |                   |
| P4             | yes       |             |              |                   |
| P5             | yes       |             |              |                   |

Assign participants to groups before the session. Suggested split: P1–P2 without tool, P3–P5 with tool.

---

## Analyst Notes

**Ground truth:** The circuit contains a bug — the CNOT control and target are reversed (`cx(1, 0)` should be `cx(0, 1)`). Qubit 1 starts in |0⟩, so the CNOT never fires, and the result is |00⟩ and |10⟩ in equal superposition instead of the Bell state |00⟩ and |11⟩.

**Metrics to compare between groups:**

- **Detection rate** — proportion of participants who spotted the bug (spotted_bug = yes)
- **Mean time** — average seconds to reach a decision; lower suggests the tool reduces cognitive load
- **Mean confidence** — average self-rated confidence; higher suggests the tool helps users feel certain

**Interpretation caveat:** N=5 is too small for statistical inference. Frame findings as *preliminary evidence motivating future work*, not as conclusive results. Reviewers respect honesty; do not overclaim.

**Paper framing suggestion:** "In a preliminary study (N=5), participants using the tool detected the injected bug in X% of trials vs Y% in the unassisted group, and reported higher mean confidence (tool: Z, no tool: W). These results are indicative and motivate a larger controlled evaluation."
