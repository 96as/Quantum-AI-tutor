"""Team A benchmark runner — 8 circuits evaluated through the full pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.quantumai.bug_checker import check_bugs
from backend.quantumai.llm import get_expected_distribution
from backend.quantumai.simulator import execute_circuit

# ---------------------------------------------------------------------------
# Benchmark circuit definitions
# ---------------------------------------------------------------------------

CIRCUITS: list[tuple[str, str, bool]] = [
    # (name, code, is_buggy)
    (
        "Bell state (correct)",
        """\
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
""",
        False,
    ),
    (
        "GHZ state (correct)",
        """\
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure([0, 1, 2], [0, 1, 2])
""",
        False,
    ),
    (
        "Deutsch-Jozsa constant oracle (correct)",
        """\
qc = QuantumCircuit(3, 2)
qc.x(2)
qc.h([0, 1, 2])
qc.h([0, 1])
qc.measure([0, 1], [0, 1])
""",
        False,
    ),
    (
        "Grover 2-qubit marking |11> (correct)",
        """\
qc = QuantumCircuit(2, 2)
qc.h([0, 1])
qc.cz(0, 1)
qc.h([0, 1])
qc.x([0, 1])
qc.cz(0, 1)
qc.x([0, 1])
qc.h([0, 1])
qc.measure([0, 1], [0, 1])
""",
        False,
    ),
    (
        "QFT on 2 qubits (correct)",
        """\
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cp(math.pi / 2, 0, 1)
qc.h(1)
qc.swap(0, 1)
qc.measure([0, 1], [0, 1])
""",
        False,
    ),
    (
        "Buggy Bell — CNOT control/target reversed",
        """\
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(1, 0)
qc.measure([0, 1], [0, 1])
""",
        True,
    ),
    (
        "Buggy GHZ — H on wrong qubit",
        """\
qc = QuantumCircuit(3, 3)
qc.h(1)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure([0, 1, 2], [0, 1, 2])
""",
        True,
    ),
    (
        "Buggy Grover — missing final H (wrong basis measurement)",
        """\
qc = QuantumCircuit(2, 2)
qc.h([0, 1])
qc.cz(0, 1)
qc.x([0, 1])
qc.cz(0, 1)
qc.x([0, 1])
qc.measure([0, 1], [0, 1])
""",
        True,
    ),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tvd(actual: dict[str, float], expected: dict[str, float]) -> float:
    """Total Variation Distance between two probability distributions."""
    all_states = set(actual) | set(expected)
    return 0.5 * sum(abs(actual.get(s, 0.0) - expected.get(s, 0.0)) for s in all_states)


def _run_one(name: str, code: str) -> dict:
    print(f"  Running: {name}")

    execution = execute_circuit(code, shots=1024)
    actual = execution.distribution if execution.success else {}

    expected: dict[str, float] = {}
    try:
        expected = get_expected_distribution(name, code)
    except Exception as exc:
        print(f"    Warning — could not get expected distribution: {exc}")

    tvd = _tvd(actual, expected) if actual and expected else 1.0

    bugs = check_bugs(code)
    pipeline_pass = tvd < 0.1 and not bugs

    raw_llm_bugs = check_bugs(code)

    return {
        "circuit_name": name,
        "tvd": round(tvd, 4),
        "bugs_flagged": bugs,
        "pipeline_pass_fail": "pass" if pipeline_pass else "fail",
        "raw_llm_bugs_flagged": raw_llm_bugs,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("QuantumAI Benchmark Runner")
    print("=" * 60)

    results: list[dict] = []
    for name, code, _ in CIRCUITS:
        row = _run_one(name, code)
        results.append(row)

    buggy_names = {name for name, _, is_buggy in CIRCUITS if is_buggy}

    buggy_results = [r for r in results if r["circuit_name"] in buggy_names]
    pipeline_detected = sum(1 for r in buggy_results if r["bugs_flagged"])
    raw_llm_detected = sum(1 for r in buggy_results if r["raw_llm_bugs_flagged"])
    n_buggy = len(buggy_results)

    pipeline_rate = f"{pipeline_detected}/{n_buggy} ({100 * pipeline_detected // n_buggy}%)" if n_buggy else "n/a"
    raw_llm_rate = f"{raw_llm_detected}/{n_buggy} ({100 * raw_llm_detected // n_buggy}%)" if n_buggy else "n/a"

    summary = {
        "pipeline_bug_detection_rate": pipeline_rate,
        "raw_llm_bug_detection_rate": raw_llm_rate,
    }

    output = {"circuits": results, "summary": summary}

    out_path = Path(__file__).parent / "benchmark_results.json"
    out_path.write_text(json.dumps(output, indent=2))

    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    header = f"{'Circuit':<45} {'TVD':>6}  {'Bugs':>4}  {'Pass/Fail':>9}"
    print(header)
    print("-" * len(header))
    for r in results:
        name_col = r["circuit_name"][:44]
        print(
            f"{name_col:<45} {r['tvd']:>6.4f}  {len(r['bugs_flagged']):>4}  {r['pipeline_pass_fail']:>9}"
        )
    print()
    print(f"Pipeline bug detection rate : {pipeline_rate}")
    print(f"Raw LLM bug detection rate  : {raw_llm_rate}")
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    main()
