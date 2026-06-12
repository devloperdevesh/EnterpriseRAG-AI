"""
LLM Integration — Ollama HTTP Client
=====================================
Sends prompts to a locally running Ollama server and returns generated answers.

The `generate_answer` function is wrapped with the `with_retry` decorator from
`app.reliability.retry_handler` so that transient network errors (connection
refused, timeouts) are automatically retried with exponential backoff before
surfacing an error to the caller.
"""

import requests

from app.reliability.retry_handler import with_retry

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3:8b"


@with_retry(
    max_retries=3,
    base_delay=1.0,
    max_delay=8.0,
    backoff_factor=2.0,
    jitter=True,
    exceptions=(
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ),
)
def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer from Ollama using retrieved document context.

    The function is decorated with `@with_retry` which means:
    - On a ConnectionError or Timeout, it will automatically retry up to 3 times.
    - Each retry waits longer than the previous one (exponential backoff).
    - Random jitter is added to each delay to prevent multiple simultaneous
      retries hitting the server at the same moment (thundering herd).

    Args:
        context:  The relevant document chunk retrieved from the vector store.
        question: The user's original question.

    Returns:
        A string answer from the LLM, or a user-friendly error message
        if all retries are exhausted.
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
        return data.get("response", "No response from AI model.")

    except requests.exceptions.HTTPError as e:
        # HTTP errors (4xx, 5xx) are not retried — they indicate a real problem.
        return f"Ollama returned an HTTP error: {e}"

    except Exception as e:
        # Any remaining errors after all retries are exhausted land here.
        return f"AI generation error: {str(e)}"
