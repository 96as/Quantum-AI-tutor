"""Plain-language explanation of Qiskit circuit results using Claude."""

from __future__ import annotations

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

_FALLBACK = "Explanation unavailable."


def _client() -> Anthropic:
    load_dotenv()
    key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("API_KEY")
    if not key:
        raise RuntimeError("Claude API key missing")
    return Anthropic(api_key=key)


def _model() -> str:
    load_dotenv()
    return os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def explain(code: str, actual: dict, expected: dict) -> str:
    """Generate a 3-paragraph plain-language explanation of a circuit's results.

    Paragraph 1: what the circuit does conceptually.
    Paragraph 2: what the actual output distribution means and whether it matches expected.
    Paragraph 3: any discrepancy between actual and expected, and what might be causing it.

    Returns a fallback string on error or empty code.
    """
    if not code.strip():
        return _FALLBACK

    system = (
        "You explain quantum computing results in plain language for a technically curious but "
        "non-expert audience. Write exactly 3 paragraphs separated by a blank line. "
        "Paragraph 1: what the circuit does conceptually. "
        "Paragraph 2: what the actual output distribution means and whether it matches the expected distribution. "
        "Paragraph 3: any discrepancy between actual and expected and what might be causing it, "
        "or confirm they match if the distributions are close. "
        "Be concrete and specific. Do not use LaTeX notation. Do not use bullet points or headers."
    )
    user = (
        "Explain these quantum circuit results:\n\n"
        f"Code:\n{code}\n\n"
        f"Actual measurement distribution: {json.dumps(actual)}\n"
        f"Expected ideal distribution: {json.dumps(expected)}"
    )

    try:
        message = _client().messages.create(
            model=_model(),
            max_tokens=900,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(
            getattr(block, "text", "")
            for block in getattr(message, "content", [])
        ).strip()
        return text or _FALLBACK
    except Exception:
        return _FALLBACK
