"""QuantumAI backend — generation, simulation, verification, and explanation."""

from backend.quantumai.bug_checker import check_bugs
from backend.quantumai.explainer import explain
from backend.quantumai.llm import generate_circuit, get_expected_distribution
from backend.quantumai.models import ExecutionResult, GeneratedCircuit, PipelineResult
from backend.quantumai.pipeline import run_pipeline
from backend.quantumai.simulator import execute_circuit

__all__ = [
    "ExecutionResult",
    "GeneratedCircuit",
    "PipelineResult",
    "check_bugs",
    "execute_circuit",
    "explain",
    "generate_circuit",
    "get_expected_distribution",
    "run_pipeline",
]
