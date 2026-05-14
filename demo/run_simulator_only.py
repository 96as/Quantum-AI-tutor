"""Run Team A's simulator without Claude API access."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.quantumai import execute_circuit


BELL_CODE = """
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""


def main() -> None:
    """Execute a hard-coded Bell state and print JSON output."""
    result = execute_circuit(BELL_CODE, shots=1024)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
