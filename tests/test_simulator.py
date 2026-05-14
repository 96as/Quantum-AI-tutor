from backend.quantumai.simulator import execute_circuit


def test_execute_circuit_runs_bell_state_distribution():
    code = """
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""

    result = execute_circuit(code, shots=512)

    assert result.success is True
    assert result.error is None
    assert set(result.distribution).issubset({"00", "11"})
    assert result.distribution["00"] > 0.35
    assert result.distribution["11"] > 0.35
    assert abs(sum(result.distribution.values()) - 1.0) < 0.000001


def test_execute_circuit_returns_controlled_error_for_invalid_code():
    result = execute_circuit("qc = missing_name()", shots=128)

    assert result.success is False
    assert result.distribution == {}
    assert result.counts == {}
    assert "missing_name" in result.error
