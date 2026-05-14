# SE455-chatbot-group-12

QuantumAI is an AI-assisted quantum programming tool. Team A owns the backend
generation and simulation pipeline: prompt -> Claude-generated Qiskit code ->
Qiskit Aer execution -> expected distribution -> JSON contract.

## Team A backend setup

Install the Python dependencies from the repo root:

```bash
python3 -m pip install -r requirements.txt
```

Create a local `.env` file with your Claude API key:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
```

The backend also supports the existing `API_KEY` name as a fallback.

## Team A public API

Import the pipeline functions from `backend.quantumai`:

```python
from backend.quantumai import execute_circuit, generate_circuit, get_expected_distribution, run_pipeline
```

The main integration function is:

```python
result = run_pipeline("Make me a Bell state", shots=1024)
payload = result.to_dict()
```

Successful output follows this JSON contract:

```json
{
  "prompt": "Make me a Bell state",
  "algorithm": "Bell state",
  "code": "from qiskit import QuantumCircuit\n...",
  "shots": 1024,
  "actual_distribution": {
    "00": 0.51,
    "11": 0.49
  },
  "expected_distribution": {
    "00": 0.5,
    "11": 0.5
  },
  "status": "ok",
  "errors": []
}
```

## Run examples

Run the simulator without Claude:

```bash
python3 demo/run_simulator_only.py
```

Run the full Claude + Qiskit Aer pipeline:

```bash
python3 demo/run_team_a_pipeline.py
```

Run tests:

```bash
python3 -m pytest -q
```
