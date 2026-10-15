
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


def get_token_usage(response):
    """Extract available token counts from the Gemini response."""
    usage = getattr(response, "usage_metadata", None)

    if usage is None:
        return {}

    usage_details = {}

    input_tokens = getattr(usage, "prompt_token_count", None)
    output_tokens = getattr(usage, "candidates_token_count", None)
    total_tokens = getattr(usage, "total_token_count", None)

    if input_tokens is not None:
        usage_details["input"] = input_tokens

    if output_tokens is not None:
        usage_details["output"] = output_tokens

    if total_tokens is not None:
        usage_details["total"] = total_tokens

    return usage_details


@app.get("/health")
def health():
    """Return application health and version."""
    return jsonify(
        status="ok",
        version=os.getenv("APP_VERSION", "local"),
    )


@app.post("/chat")
def chat():
    """Call Gemini and capture the generation in Langfuse."""

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

            # Build the exact prompt that will be sent to Gemini.
            prompt = (
                "Answer clearly and briefly.\n"
                f"Context: {context}\n"
                f"Question: {valid_message}"
            )

            model_name = os.getenv(
                "GEMINI_MODEL",
                "gemini-3.5-flash-lite",
            )

            client = get_gemini_client()

            # Langfuse records generation input, output and duration.
            with langfuse.start_as_current_observation(
                as_type="generation",
                name="gemini-generation",
                model=model_name,
                input=prompt,
            ) as generation:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                reply = response.text or "The model returned no text."

                # Record the completion.
                generation.update(output=reply)

                # Record token usage when Gemini provides it.
                usage_details = get_token_usage(response)

                if usage_details:
                    generation.update(
                        usage_details=usage_details
                    )

            with langfuse.start_as_current_observation(
                as_type="span",
                name="format-response",
            ) as span:
                result = {"reply": reply}
                span.update(output="Response formatted")

            trace.update(output=result)

        # Send pending observations to Langfuse before responding.
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
    serve(app, host="127.0.0.1", port=8080)
