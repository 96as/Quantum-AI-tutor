"""Bridge Team A pipeline results into Team C's Streamlit display shape."""

from __future__ import annotations

from typing import Any, Callable

from backend.quantumai import run_pipeline


PipelineCallable = Callable[[str, int], Any]


def adapt_pipeline_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Add temporary UI fields around Team A's backend contract.

    Team B will eventually replace the verification, bug, and explanation fields.
    For now, this keeps Team C's panels working with real generated code and
    simulated distributions.
    """
    status = payload.get("status")
    errors = payload.get("errors") or []
    verification_passed = status == "ok"
    algorithm = payload.get("algorithm") or "the generated circuit"

    if verification_passed:
        verification_message = "Generation and simulation completed."
        explanation = (
            f"Team A generated and simulated {algorithm}. "
            "The chart compares the measured Aer distribution with the expected "
            "distribution returned by Claude. Team B will add deeper verification, "
            "bug flags, and a plain-language explanation."
        )
    else:
        verification_message = "; ".join(str(error) for error in errors) or "Pipeline failed."
        explanation = "The backend could not complete this request."

    return {
        "code": payload.get("code", ""),
        "actual_distribution": payload.get("actual_distribution", {}),
        "expected_distribution": payload.get("expected_distribution", {}),
        "verification_passed": verification_passed,
        "verification_message": verification_message,
        "bugs": [],
        "explanation": explanation,
    }


def result_from_prompt(
    prompt: str,
    shots: int = 1024,
    pipeline: PipelineCallable = run_pipeline,
) -> dict[str, Any]:
    """Run Team A's pipeline and return the shape expected by Team C's UI."""
    pipeline_result = pipeline(prompt, shots)
    if hasattr(pipeline_result, "to_dict"):
        payload = pipeline_result.to_dict()
    else:
        payload = dict(pipeline_result)
    return adapt_pipeline_result(payload)
