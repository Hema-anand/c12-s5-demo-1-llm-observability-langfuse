
"""Flask application with Gemini and Langfuse observability."""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from google import genai
from langfuse import get_client
from waitress import serve

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)

langfuse = get_client()


def get_gemini_client():
    """Create a Gemini client using the configured API key."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=api_key)


@app.get("/health")
def health():
    """Return application health and version."""
    return jsonify(
        status="ok",
        version=os.getenv("APP_VERSION", "local"),
    )


@app.post("/chat")
def chat():
    """Validate input, call Gemini, and capture a Langfuse trace."""
    body = request.get_json(silent=True)
    message = body.get("message") if isinstance(body, dict) else None

    if not isinstance(message, str) or not message.strip():
        return jsonify(
            error="Provide a non-empty message string."
        ), 400

    message = message.strip()

    if len(message) > 1000:
        return jsonify(
            error="Message must be at most 1000 characters."
        ), 400

    try:
        with langfuse.start_as_current_observation(
            as_type="span",
            name="chat-request",
            input={"message": message},
        ) as trace:

            with langfuse.start_as_current_observation(
                as_type="span",
                name="validate-input",
            ) as span:
                valid_message = message
                span.update(output="Input validated")

            with langfuse.start_as_current_observation(
                as_type="span",
                name="retrieve-context",
            ) as span:
                # Placeholder for this observability demo.
                context = "No external documents were retrieved."
                span.update(output=context)

            with langfuse.start_as_current_observation(
                as_type="generation",
                name="gemini-generation",
                model=os.getenv(
                    "GEMINI_MODEL", "gemini-flash-latest"
                ),
                input=valid_message,
            ) as generation:

                # Used later in Demo 2 to create a slow span.
                if os.getenv("DEMO_SLOW_REQUEST") == "true":
                    import time
                    time.sleep(2)

                client = get_gemini_client()
                response = client.models.generate_content(
                    model=os.getenv(
                        "GEMINI_MODEL", "gemini-flash-latest"
                    ),
                    contents=(
                        "Answer clearly and briefly.\n"
                        f"Context: {context}\n"
                        f"Question: {valid_message}"
                    ),
                )

                reply = response.text or "The model returned no text."
                generation.update(output=reply)

            with langfuse.start_as_current_observation(
                as_type="span",
                name="format-response",
            ) as span:
                result = {"reply": reply}
                span.update(output="Response formatted")

            trace.update(output=result)

        langfuse.flush()
        return jsonify(result)

    except Exception:
        app.logger.exception("Chat request failed")
        langfuse.flush()
        return jsonify(
            error="The request could not be completed."
        ), 502


if __name__ == "__main__":
    app.logger.info("Application starting on port 8080")
    serve(app, host="0.0.0.0", port=8080)
