import pytest

from backend.quantumai.llm import LLMResponseError, parse_expected_distribution


def test_parse_expected_distribution_accepts_strict_json():
    raw = """
{
  "00": 0.5,
  "11": 0.5
}
"""

    assert parse_expected_distribution(raw) == {"00": 0.5, "11": 0.5}


def test_parse_expected_distribution_rejects_invalid_json():
    with pytest.raises(LLMResponseError, match="valid JSON"):
        parse_expected_distribution("The expected states are 00 and 11.")


def test_parse_expected_distribution_rejects_non_numeric_probabilities():
    with pytest.raises(LLMResponseError, match="numeric"):
        parse_expected_distribution('{"00": "half", "11": 0.5}')
