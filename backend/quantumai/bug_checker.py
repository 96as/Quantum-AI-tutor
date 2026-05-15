"""Qiskit circuit bug pattern checker using Paltenghi & Pradel taxonomy."""

from __future__ import annotations

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

_BUG_PATTERNS = [
    "Missing measurement — qubits are never measured",
    "Wrong basis measurement — measuring in Z when the circuit uses X or Y basis gates",
    "Incorrect initial state — assuming |0⟩ but the circuit resets or prepares differently",
    "Gate on wrong qubit — a gate is applied to a qubit index that doesn't match the intended target",
    "Missing barrier — operations that should be separated are fused by the optimizer",
    "Incorrect entanglement — CNOT control/target reversed, or entanglement not established before measurement",
]


def _client() -> Anthropic:
    load_dotenv()
    key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("API_KEY")
    if not key:
        raise RuntimeError("Claude API key missing")
    return Anthropic(api_key=key)


def _model() -> str:
    load_dotenv()
    return os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def _parse_bug_list(text: str) -> list[str]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines and lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner).strip()
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if isinstance(item, str)]


def check_bugs(code: str) -> list[str]:
    """Check Qiskit code against 6 Paltenghi & Pradel bug patterns.

    Returns a list of violated pattern names. Empty list if none found or on error.
    """
    if not code.strip():
        return []

    patterns_block = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(_BUG_PATTERNS))
    system = (
        "You are a Qiskit bug detector. Analyse the provided circuit for specific bug patterns. "
        "Respond with ONLY a valid JSON array of strings. Each string must be the short name of a "
        "violated pattern — the text before the em dash (—). "
        'Return an empty array [] if no patterns are violated. '
        "Do not include prose, markdown fences, or any text outside the JSON array."
    )
    user = (
        f"Check this Qiskit code for the following bug patterns:\n\n"
        f"{patterns_block}\n\n"
        f"Code:\n{code}\n\n"
        f"Return ONLY a JSON array of violated short pattern names, e.g. "
        f'["Missing measurement", "Incorrect entanglement"] or []'
    )

    try:
        message = _client().messages.create(
            model=_model(),
            max_tokens=512,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = "".join(
            getattr(block, "text", "")
            for block in getattr(message, "content", [])
        )
        return _parse_bug_list(raw)
    except Exception:
        return []
