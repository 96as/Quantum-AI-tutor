# QuantumAI

QuantumAI is an AI-assisted quantum programming tool for learning and testing
small Qiskit circuits. The current app connects Team C's Streamlit UI to Team
A's backend pipeline:

```text
user prompt -> Claude generates Qiskit code -> Qiskit Aer simulates the circuit
-> Claude returns expected distribution -> Streamlit displays code + chart
```

Team B can plug verification, bug-pattern checks, and richer explanations into
the same result object later.

## Setup

Install the Python dependencies from the repo root:

```bash
python3 -m pip install -r requirements.txt
```

Create a local `.env` file with your Claude API key:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-sonnet-4-6
```

The backend also supports the existing `API_KEY` name as a fallback. If the
default model is unavailable for your Anthropic account, set `ANTHROPIC_MODEL`
to one of the IDs returned by Anthropic's model list endpoint.

## Run the UI

Start Streamlit from the repo root:

```bash
streamlit run app.py
```

If port `8501` is already busy:

```bash
streamlit run app.py --server.port 8503
```

Open the URL Streamlit prints, then try:

```text
Make me a Bell state
```

or:

```text
grovers alg marking 011
```

Expected result: generated Qiskit code on the left, actual vs expected output
distribution on the right, and a success/error message below.

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

## UI integration contract

`app.py` calls `ui_adapter.result_from_prompt(prompt)`. The adapter calls
Team A's `run_pipeline()` and adds temporary fields that Team C's UI expects:

```json
{
  "code": "from qiskit import QuantumCircuit\n...",
  "actual_distribution": {"00": 0.51, "11": 0.49},
  "expected_distribution": {"00": 0.5, "11": 0.5},
  "verification_passed": true,
  "verification_message": "Generation and simulation completed.",
  "bugs": [],
  "explanation": "Temporary Team A explanation text"
}
```

Team B should replace `verification_passed`, `verification_message`, `bugs`,
and `explanation` with real verification and bug-checking output. Team A owns
generation, simulation, and expected-distribution retrieval.

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

## Common errors

- `Claude API key missing`: `.env` does not contain `ANTHROPIC_API_KEY` or
  `API_KEY`.
- `401 invalid x-api-key`: the key exists but Anthropic rejected it.
- `404 model: ...`: set `ANTHROPIC_MODEL` to an available Anthropic model, such
  as `claude-sonnet-4-6`.
- `Generated code must define qc`: Claude did not create a `qc =
  QuantumCircuit(...)` variable; retry with a clearer prompt.
- `LLM response must be valid JSON`: Claude returned malformed or truncated
  JSON for the expected distribution. The parser handles strict, fenced, and
  embedded JSON, but a truly incomplete response must be retried.
- `Import of '...' is not allowed`: generated code tried to import a blocked
  package. The simulator intentionally allows only safe quantum/math imports.

## Project layout

- `app.py`: Streamlit UI from Team C, now wired to the backend.
- `ui_adapter.py`: adapter between Team A's backend contract and Team C's UI
  display fields.
- `backend/quantumai/`: Team A backend package.
- `demo/`: CLI demos for simulator-only and full pipeline runs.
- `tests/`: regression tests for backend simulation, LLM parsing, pipeline, and
  UI adapter behavior.
