"""End-to-end Team A pipeline: generate, simulate, and return distributions."""

from __future__ import annotations

from backend.quantumai.llm import generate_circuit, get_expected_distribution
from backend.quantumai.models import PipelineResult
from backend.quantumai.simulator import execute_circuit


def run_pipeline(prompt: str, shots: int = 1024) -> PipelineResult:
    """Run the Team A generation and simulation pipeline for one prompt."""
    try:
        generated = generate_circuit(prompt)
    except Exception as exc:
        return PipelineResult(
            prompt=prompt,
            algorithm=None,
            code="",
            shots=shots,
            actual_distribution={},
            expected_distribution={},
            status="error",
            errors=[str(exc)],
        )

    errors: list[str] = []
    execution = execute_circuit(generated.code, shots=shots)
    if not execution.success:
        errors.append(execution.error or "Circuit execution failed")

    expected_distribution = {}
    if execution.success:
        try:
            expected_distribution = get_expected_distribution(prompt, generated.code)
        except Exception as exc:
            errors.append(str(exc))

    return PipelineResult(
        prompt=prompt,
        algorithm=generated.algorithm,
        code=generated.code,
        shots=shots,
        actual_distribution=execution.distribution if execution.success else {},
        expected_distribution=expected_distribution,
        status="ok" if not errors else "error",
        errors=errors,
    )
