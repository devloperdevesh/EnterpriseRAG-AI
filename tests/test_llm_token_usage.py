"""Tests for token usage extraction in app.rag.llm (issue #117).

The Ollama HTTP call is mocked so these run hermetically without a running
Ollama server.
"""

import requests

from app.rag import llm


class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"status {self.status_code}")

    def json(self):
        return self._json_data


def test_generate_answer_with_usage_extracts_token_counts(monkeypatch):
    def fake_post(*_args, **_kwargs):
        return _FakeResponse(
            {
                "response": "Refunds are processed within 14 days.",
                "prompt_eval_count": 120,
                "eval_count": 18,
            }
        )

    monkeypatch.setattr(llm.requests, "post", fake_post)

    answer, usage = llm.generate_answer_with_usage("some context", "refund policy?")

    assert answer == "Refunds are processed within 14 days."
    assert usage == {
        "prompt_tokens": 120,
        "completion_tokens": 18,
        "total_tokens": 138,
    }


def test_generate_answer_with_usage_missing_counts_defaults_to_zero(monkeypatch):
    def fake_post(*_args, **_kwargs):
        return _FakeResponse({"response": "answer with no usage fields"})

    monkeypatch.setattr(llm.requests, "post", fake_post)

    answer, usage = llm.generate_answer_with_usage("ctx", "q")

    assert answer == "answer with no usage fields"
    assert usage == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def test_generate_answer_with_usage_timeout_returns_zero_usage(monkeypatch):
    def fake_post(*_args, **_kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(llm.requests, "post", fake_post)

    answer, usage = llm.generate_answer_with_usage("ctx", "q")

    assert answer == "AI model timeout. Please try again."
    assert usage == {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def test_generate_answer_with_usage_connection_error(monkeypatch):
    def fake_post(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(llm.requests, "post", fake_post)

    answer, usage = llm.generate_answer_with_usage("ctx", "q")

    assert "Ollama server not running" in answer
    assert usage["total_tokens"] == 0


def test_generate_answer_backward_compatible_returns_string_only(monkeypatch):
    def fake_post(*_args, **_kwargs):
        return _FakeResponse(
            {"response": "ok", "prompt_eval_count": 5, "eval_count": 5}
        )

    monkeypatch.setattr(llm.requests, "post", fake_post)

    answer = llm.generate_answer("ctx", "q")

    assert answer == "ok"
    assert isinstance(answer, str)
