"""Claude API helpers for Qiskit generation and expected distributions."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from backend.quantumai.models import Distribution, GeneratedCircuit

DEFAULT_MODEL = "claude-sonnet-4-6"
EXPECTED_DISTRIBUTION_MAX_TOKENS = 1200


class LLMResponseError(ValueError):
    """Raised when the LLM response cannot be parsed into the required shape."""


def _api_key() -> str:
    load_dotenv()
    key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("API_KEY")
    if not key:
        raise RuntimeError("Claude API key missing")
    return key


def _client() -> Anthropic:
    return Anthropic(api_key=_api_key())


def _model() -> str:
    load_dotenv()
    return os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)


def _message_text(message: Any) -> str:
    parts: list[str] = []
    for block in getattr(message, "content", []):
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json|python)?\s*(.*?)\s*```", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def _candidate_json_objects(text: str) -> list[str]:
    candidates = [_strip_markdown_fence(text)]
    candidates.extend(
        match.group(1).strip()
        for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    )

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            _, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        candidates.append(text[index : index + end])
    return candidates


def _extract_json_object(text: str) -> dict[str, Any]:
    for raw in _candidate_json_objects(text):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            raise LLMResponseError("LLM response must be a JSON object")
        return parsed
    raise LLMResponseError("LLM response must be valid JSON")


def parse_expected_distribution(text: str) -> Distribution:
    """Parse strict JSON into a normalized bitstring probability mapping."""
    parsed = _extract_json_object(text)
    distribution: Distribution = {}
    for state, probability in parsed.items():
        if not isinstance(state, str) or not re.fullmatch(r"[01]+", state):
            raise LLMResponseError("Expected distribution keys must be bitstrings")
        if not isinstance(probability, (int, float)):
            raise LLMResponseError("Expected distribution values must be numeric")
        value = float(probability)
        if value < 0.0 or value > 1.0:
            raise LLMResponseError("Expected distribution values must be between 0 and 1")
        distribution[state] = value
    if not distribution:
        raise LLMResponseError("Expected distribution cannot be empty")
    return distribution


def _parse_generated_circuit(prompt: str, text: str) -> GeneratedCircuit:
    raw = _strip_markdown_fence(text)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return GeneratedCircuit(prompt=prompt, code=raw, algorithm=None, notes="")

    if not isinstance(parsed, dict):
        raise LLMResponseError("Generated circuit response must be a JSON object")
    code = parsed.get("code")
    if not isinstance(code, str) or not code.strip():
        raise LLMResponseError("Generated circuit response must include code")
    algorithm = parsed.get("algorithm")
    notes = parsed.get("notes", "")
    return GeneratedCircuit(
        prompt=prompt,
        code=code.strip(),
        algorithm=algorithm if isinstance(algorithm, str) else None,
        notes=notes if isinstance(notes, str) else "",
    )


def generate_circuit(prompt: str) -> GeneratedCircuit:
    """Generate executable Qiskit code from a natural-language prompt."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    system = (
        "You generate small educational Qiskit circuits. Return strict JSON only "
        "with keys: algorithm, code, notes. The code must define a variable named "
        "qc containing a QuantumCircuit. Use QuantumCircuit from qiskit. Do not use "
        "files, network calls, subprocesses, input(), or external services. Keep "
        "circuits small enough for local Qiskit Aer simulation."
    )
    user = f"Generate Qiskit code for this request:\n{prompt}"
    message = _client().messages.create(
        model=_model(),
        max_tokens=1600,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    generated = _parse_generated_circuit(prompt, _message_text(message))
    if "qc" not in generated.code:
        raise LLMResponseError("Generated code must define qc")
    return generated


def get_expected_distribution(prompt: str, code: str) -> Distribution:
    """Ask Claude for the ideal expected measurement distribution as JSON."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    if not code.strip():
        raise ValueError("Code cannot be empty")

    system = (
        "You identify ideal quantum measurement distributions for small Qiskit "
        "circuits. Your entire response must be one compact JSON object and "
        "nothing else. Use bitstring keys and numeric probabilities, for example "
        '{"00": 0.5, "11": 0.5}. Do not include prose, markdown, equations, '
        "analysis, code fences, or explanations."
    )
    user = (
        "Given this user request and generated Qiskit code, return the ideal "
        "expected measurement distribution. Respond with only the final JSON "
        "object, starting with { and ending with }.\n\n"
        f"Request:\n{prompt}\n\nCode:\n{code}"
    )
    message = _client().messages.create(
        model=_model(),
        max_tokens=EXPECTED_DISTRIBUTION_MAX_TOKENS,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return parse_expected_distribution(_message_text(message))
