"""CLI script to collect user study results and print a summary."""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

RESULTS_FILE = Path(__file__).parent / "results.csv"
FIELDNAMES = ["participant_id", "used_tool", "spotted_bug", "time_seconds", "confidence_1_to_5"]
N_PARTICIPANTS = 5


def _ask(prompt: str, valid: set[str] | None = None) -> str:
    while True:
        value = input(prompt).strip().lower()
        if valid is None or value in valid:
            return value
        print(f"  Please enter one of: {', '.join(sorted(valid))}")


def _ask_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if lo <= value <= hi:
                return value
        except ValueError:
            pass
        print(f"  Please enter a whole number between {lo} and {hi}.")


def _ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value >= 0:
                return value
        except ValueError:
            pass
        print("  Please enter a non-negative number (seconds).")


def collect() -> list[dict]:
    rows: list[dict] = []
    print("\n=== QuantumAI User Study — Data Entry ===")
    print(f"You will enter results for {N_PARTICIPANTS} participants.\n")

    for i in range(1, N_PARTICIPANTS + 1):
        pid = f"P{i}"
        print(f"--- Participant {pid} ---")
        used_tool = _ask("  Used tool? (y/n): ", {"y", "n"})
        spotted_bug = _ask("  Spotted bug? (y/n): ", {"y", "n"})
        time_sec = _ask_float("  Time to decision (seconds): ")
        confidence = _ask_int("  Confidence (1–5): ", 1, 5)
        rows.append({
            "participant_id": pid,
            "used_tool": "yes" if used_tool == "y" else "no",
            "spotted_bug": "yes" if spotted_bug == "y" else "no",
            "time_seconds": time_sec,
            "confidence_1_to_5": confidence,
        })
        print()
    return rows


def save(rows: list[dict]) -> None:
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_FILE.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results saved to: {RESULTS_FILE}")


def summarise(rows: list[dict]) -> None:
    tool_rows = [r for r in rows if r["used_tool"] == "yes"]
    no_tool_rows = [r for r in rows if r["used_tool"] == "no"]

    def _detection_rate(group: list[dict]) -> str:
        if not group:
            return "n/a"
        n = sum(1 for r in group if r["spotted_bug"] == "yes")
        return f"{n}/{len(group)} ({100 * n // len(group)}%)"

    def _mean(group: list[dict], key: str) -> str:
        if not group:
            return "n/a"
        values = [float(r[key]) for r in group]
        return f"{statistics.mean(values):.1f}"

    print("\n=== Summary ===")
    print(f"{'Metric':<35} {'With tool':>12} {'Without tool':>14}")
    print("-" * 63)
    print(f"{'Detection rate':<35} {_detection_rate(tool_rows):>12} {_detection_rate(no_tool_rows):>14}")
    print(f"{'Mean time (seconds)':<35} {_mean(tool_rows, 'time_seconds'):>12} {_mean(no_tool_rows, 'time_seconds'):>14}")
    print(f"{'Mean confidence (1–5)':<35} {_mean(tool_rows, 'confidence_1_to_5'):>12} {_mean(no_tool_rows, 'confidence_1_to_5'):>14}")
    print()
    print("Note: N=5 is preliminary evidence only — do not over-interpret.")


def main() -> None:
    try:
        rows = collect()
    except KeyboardInterrupt:
        print("\nAborted — no data saved.")
        sys.exit(1)

    save(rows)
    summarise(rows)


if __name__ == "__main__":
    main()
