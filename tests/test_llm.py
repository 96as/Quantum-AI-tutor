import pytest

from backend.quantumai.llm import DEFAULT_MODEL, LLMResponseError, _model, parse_expected_distribution


def test_parse_expected_distribution_accepts_strict_json():
    raw = """
{
  "00": 0.5,
  "11": 0.5
}
"""

    assert parse_expected_distribution(raw) == {"00": 0.5, "11": 0.5}


def test_parse_expected_distribution_accepts_fenced_json_with_surrounding_text():
    raw = """
The expected distribution is:

```json
{
  "00": 0.5,
  "11": 0.5
}
```
"""

    assert parse_expected_distribution(raw) == {"00": 0.5, "11": 0.5}


def test_parse_expected_distribution_accepts_embedded_json_object():
    raw = 'For this circuit, use {"00": 0.5, "11": 0.5} as the expected distribution.'

    assert parse_expected_distribution(raw) == {"00": 0.5, "11": 0.5}


def test_parse_expected_distribution_rejects_invalid_json():
    with pytest.raises(LLMResponseError, match="valid JSON"):
        parse_expected_distribution("The expected states are 00 and 11.")


def test_parse_expected_distribution_rejects_non_numeric_probabilities():
    with pytest.raises(LLMResponseError, match="numeric"):
        parse_expected_distribution('{"00": "half", "11": 0.5}')


def test_model_uses_supported_default_when_env_is_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)

    assert DEFAULT_MODEL == "claude-sonnet-4-6"
    assert _model() == "claude-sonnet-4-6"


def test_model_can_be_overridden_from_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

    assert _model() == "claude-sonnet-4-5-20250929"
