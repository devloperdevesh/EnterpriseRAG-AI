import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3:8b"


def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer from Ollama using retrieved document context.
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

    except requests.exceptions.Timeout:
        return "AI model timeout. Please try again."

    except requests.exceptions.ConnectionError:
        return "Ollama server not running. Please start `ollama serve`."

    except Exception as e:
        return f"AI generation error: {str(e)}"
