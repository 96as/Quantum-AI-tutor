"""Qiskit Aer execution utilities for generated circuits."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator

from backend.quantumai.models import ExecutionResult


def _safe_import(name: str, globals_: Any = None, locals_: Any = None, fromlist: Any = (), level: int = 0) -> Any:
    allowed_roots = {"qiskit", "qiskit_aer", "math", "numpy"}
    root = name.split(".", 1)[0]
    if root not in allowed_roots:
        raise ImportError(f"Import of '{name}' is not allowed")
    return __import__(name, globals_, locals_, fromlist, level)


def _execution_namespace() -> dict[str, Any]:
    builtins = {
        "__import__": _safe_import,
        "abs": abs,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "range": range,
        "set": set,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }
    return {
        "__builtins__": builtins,
        "ClassicalRegister": ClassicalRegister,
        "QuantumCircuit": QuantumCircuit,
        "QuantumRegister": QuantumRegister,
        "math": math,
        "np": np,
        "numpy": np,
    }


def _has_measurements(circuit: QuantumCircuit) -> bool:
    return any(instruction.operation.name == "measure" for instruction in circuit.data)


def _ensure_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    measured = circuit.copy()
    if not _has_measurements(measured):
        measured.measure_all()
    return measured


def _normalize_counts(counts: dict[Any, int], shots: int) -> tuple[dict[str, int], dict[str, float]]:
    normalized_counts = {str(state).replace(" ", ""): int(count) for state, count in counts.items()}
    distribution = {
        state: count / shots
        for state, count in sorted(normalized_counts.items())
    }
    return normalized_counts, distribution


def execute_circuit(code: str, shots: int = 1024) -> ExecutionResult:
    """Execute generated Qiskit code on Aer and return measurement probabilities."""
    if shots <= 0:
        return ExecutionResult(
            shots=shots,
            counts={},
            distribution={},
            success=False,
            error="shots must be positive",
        )

    namespace = _execution_namespace()
    try:
        exec(code, namespace, namespace)
        circuit = namespace.get("qc")
        if not isinstance(circuit, QuantumCircuit):
            raise ValueError("Generated code must define qc as a QuantumCircuit")

        measured = _ensure_measurements(circuit)
        simulator = AerSimulator()
        compiled = transpile(measured, simulator)
        job = simulator.run(compiled, shots=shots)
        raw_counts = job.result().get_counts()
        counts, distribution = _normalize_counts(raw_counts, shots)
        return ExecutionResult(
            shots=shots,
            counts=counts,
            distribution=distribution,
            success=True,
            error=None,
        )
    except Exception as exc:
        return ExecutionResult(
            shots=shots,
            counts={},
            distribution={},
            success=False,
            error=str(exc),
        )
