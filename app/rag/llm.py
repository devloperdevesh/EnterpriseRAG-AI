import logging
from typing import TypedDict

import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3:8b"

logger = logging.getLogger(__name__)


class TokenUsage(TypedDict):
    """Token accounting for a single LLM generation call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def _empty_usage() -> TokenUsage:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer from Ollama using retrieved document context.

    Thin wrapper around :func:`generate_answer_with_usage` kept for backward
    compatibility with existing callers that only need the answer text.
    """
    answer, _usage = generate_answer_with_usage(context, question)
    return answer


def generate_answer_with_usage(context: str, question: str) -> tuple[str, TokenUsage]:
    """Generate an answer and return it alongside token usage metadata.

    Ollama's ``/api/generate`` response (with ``stream=False``) includes
    ``prompt_eval_count`` (tokens in the prompt) and ``eval_count`` (tokens
    generated), which we surface here for observability (issue #117) without
    changing the response contract of :func:`generate_answer`.

    Returns:
        A ``(answer, usage)`` tuple. ``usage`` is all-zero when the model
        could not be reached or the call failed, so callers can always log
        a well-formed record.
    """

    prompt = f"""
You are a precise enterprise knowledge assistant.

Instructions:
- Answer strictly from the provided context.
- Do not repeat phrases.
- Keep the answer concise and professional.
- If the answer is not in the context, reply:
  "Information not found in uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )

        response.raise_for_status()
        data = response.json()

        # Ollama always returns {"response": "..."}
        answer = data.get("response", "No response from AI model.")

        prompt_tokens = int(data.get("prompt_eval_count") or 0)
        completion_tokens = int(data.get("eval_count") or 0)
        usage: TokenUsage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

        return answer, usage

    except requests.exceptions.Timeout:
        return "AI model timeout. Please try again.", _empty_usage()

    except requests.exceptions.ConnectionError:
        return "Ollama server not running. Please start `ollama serve`.", _empty_usage()

    except Exception as e:
        logger.exception("AI generation failed: %s", e)
        return "AI generation error. Please try again later.", _empty_usage()
