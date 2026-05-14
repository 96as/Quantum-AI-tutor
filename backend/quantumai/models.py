"""Data models shared by the Team A backend pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Distribution = dict[str, float]


@dataclass(frozen=True)
class GeneratedCircuit:
    """Qiskit code generated from a natural-language user prompt."""

    prompt: str
    code: str
    algorithm: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "prompt": self.prompt,
            "code": self.code,
            "algorithm": self.algorithm,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ExecutionResult:
    """Result of executing a Qiskit circuit on Qiskit Aer."""

    shots: int
    counts: dict[str, int] = field(default_factory=dict)
    distribution: Distribution = field(default_factory=dict)
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "shots": self.shots,
            "counts": self.counts,
            "distribution": self.distribution,
            "success": self.success,
            "error": self.error,
        }


@dataclass(frozen=True)
class PipelineResult:
    """Team A JSON contract returned to the frontend and later modules."""

    prompt: str
    code: str
    algorithm: str | None
    actual_distribution: Distribution
    expected_distribution: Distribution
    shots: int = 1024
    status: str = "ok"
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return the exact JSON-compatible contract shared with other teams."""
        return {
            "prompt": self.prompt,
            "algorithm": self.algorithm,
            "code": self.code,
            "shots": self.shots,
            "actual_distribution": self.actual_distribution,
            "expected_distribution": self.expected_distribution,
            "status": self.status,
            "errors": self.errors,
        }
