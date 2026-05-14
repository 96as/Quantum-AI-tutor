from backend.quantumai.models import GeneratedCircuit
from backend.quantumai.pipeline import run_pipeline


def test_run_pipeline_returns_team_contract_with_mocked_llm(monkeypatch):
    code = """
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""

    def fake_generate(prompt):
        return GeneratedCircuit(
            prompt=prompt,
            code=code,
            algorithm="Bell state",
            notes="Creates a two-qubit entangled state.",
        )

    def fake_expected(prompt, generated_code):
        return {"00": 0.5, "11": 0.5}

    monkeypatch.setattr("backend.quantumai.pipeline.generate_circuit", fake_generate)
    monkeypatch.setattr(
        "backend.quantumai.pipeline.get_expected_distribution",
        fake_expected,
    )

    result = run_pipeline("Make me a Bell state", shots=512)
    payload = result.to_dict()

    assert payload["prompt"] == "Make me a Bell state"
    assert payload["algorithm"] == "Bell state"
    assert "QuantumCircuit" in payload["code"]
    assert payload["shots"] == 512
    assert set(payload["actual_distribution"]).issubset({"00", "11"})
    assert payload["expected_distribution"] == {"00": 0.5, "11": 0.5}
    assert payload["status"] == "ok"
    assert payload["errors"] == []


def test_run_pipeline_returns_error_contract_when_generation_fails(monkeypatch):
    def fake_generate(prompt):
        raise RuntimeError("Claude API key missing")

    monkeypatch.setattr("backend.quantumai.pipeline.generate_circuit", fake_generate)

    result = run_pipeline("Make me a Bell state", shots=1024).to_dict()

    assert result == {
        "prompt": "Make me a Bell state",
        "algorithm": None,
        "code": "",
        "shots": 1024,
        "actual_distribution": {},
        "expected_distribution": {},
        "status": "error",
        "errors": ["Claude API key missing"],
    }
