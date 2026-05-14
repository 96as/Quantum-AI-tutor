"""Run Team A's full Claude + Qiskit Aer pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.quantumai import run_pipeline


def main() -> None:
    """Generate, simulate, and print the Team A JSON contract."""
    result = run_pipeline("Make me a Bell state", shots=1024)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
