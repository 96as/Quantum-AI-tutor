from ui_adapter import adapt_pipeline_result, result_from_prompt


def test_adapt_pipeline_result_adds_team_c_display_fields_for_success():
    pipeline_payload = {
        "prompt": "Make me a Bell state",
        "algorithm": "Bell state",
        "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)",
        "shots": 1024,
        "actual_distribution": {"00": 0.51, "11": 0.49},
        "expected_distribution": {"00": 0.5, "11": 0.5},
        "status": "ok",
        "errors": [],
    }

    adapted = adapt_pipeline_result(pipeline_payload)

    assert adapted["code"] == pipeline_payload["code"]
    assert adapted["actual_distribution"] == {"00": 0.51, "11": 0.49}
    assert adapted["expected_distribution"] == {"00": 0.5, "11": 0.5}
    assert adapted["verification_passed"] is True
    assert adapted["verification_message"] == "Generation and simulation completed."
    assert adapted["bugs"] == []
    assert "Bell state" in adapted["explanation"]


def test_adapt_pipeline_result_adds_error_message_for_failed_pipeline():
    pipeline_payload = {
        "prompt": "Make me a Bell state",
        "algorithm": None,
        "code": "",
        "shots": 1024,
        "actual_distribution": {},
        "expected_distribution": {},
        "status": "error",
        "errors": ["invalid x-api-key"],
    }

    adapted = adapt_pipeline_result(pipeline_payload)

    assert adapted["verification_passed"] is False
    assert adapted["verification_message"] == "invalid x-api-key"
    assert adapted["explanation"] == "The backend could not complete this request."


def test_result_from_prompt_calls_pipeline_function():
    def fake_pipeline(prompt, shots=1024):
        assert prompt == "Make me a Bell state"
        assert shots == 1024

        class Result:
            def to_dict(self):
                return {
                    "prompt": prompt,
                    "algorithm": "Bell state",
                    "code": "qc = object()",
                    "shots": shots,
                    "actual_distribution": {"00": 0.5, "11": 0.5},
                    "expected_distribution": {"00": 0.5, "11": 0.5},
                    "status": "ok",
                    "errors": [],
                }

        return Result()

    result = result_from_prompt("Make me a Bell state", pipeline=fake_pipeline)

    assert result["verification_passed"] is True
    assert result["code"] == "qc = object()"
