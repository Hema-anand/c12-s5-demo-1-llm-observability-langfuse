# Demo 1: LLM Observability with Langfuse

## Overview

In this demo, you will integrate Google Gemini with a Flask application and use Langfuse to observe how an LLM request is processed.

You will instrument the application with named spans, generate traces, and inspect the execution flow in Langfuse. The application uses a simulated retrieval stage to demonstrate trace analysis without requiring a vector database.

## Learning Outcomes

By completing this demo, you will be able to:

- Integrate a Gemini model into a Python application.
- Instrument an LLM application using Langfuse.
- Capture traces with named spans for individual processing stages.
- Inspect LLM inputs, outputs, and execution flow in Langfuse.

## Application Flow

A request to the `/chat` endpoint passes through the following stages:

1. **Validate Input:** Check whether the user message is valid.
2. **Retrieve Context:** Simulate a retrieval stage.
3. **Generate Response:** Send the message and context to Gemini.
4. **Format Response:** Prepare the response returned to the client.

Langfuse records the request trace and its associated observations, allowing you to inspect the processing stages.

## Prerequisites

Before starting, ensure that you have:

- Python 3.10 or later.
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- A Langfuse account and project with API credentials.
- The project files available in this folder.

## Project Structure

```text
demo-1-llm-observability-with-langfuse/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── tests/
    └── test_app.py
```

## Step 1: Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Open `.env` and provide your credentials:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-flash-latest

LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_BASE_URL=https://cloud.langfuse.com

APP_VERSION=local
DEMO_SLOW_REQUEST=false
```

Replace the placeholder values with your actual credentials. Use the Langfuse base URL appropriate for your project region if it differs from the example.

**Security:** Never commit your `.env` file or share your API keys.

## Step 2: Install Dependencies

Create a virtual environment if one does not already exist:

```bash
python3 -m venv .venv
```

Install the project dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## Step 3: Run the Unit Tests

Execute the test suite:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Verify that all tests pass. The tests use mocked Gemini responses, so they do not need to make actual LLM API calls.

## Step 4: Start the Application

Start the Flask application using Waitress:

```bash
.venv/bin/python app.py
```

The application listens on port `8080`.

Keep this terminal running while you test the endpoints.

## Step 5: Verify the Health Endpoint

Open another terminal and run:

```bash
curl -sS http://localhost:8080/health
```

Expected response:

```json
{
  "status": "ok",
  "version": "local"
}
```

The version may differ if `APP_VERSION` has been configured differently.

## Step 6: Send a Chat Request

Send a request to the `/chat` endpoint:

```bash
curl -sS -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain LLM observability in one sentence"}'
```

The application sends the message to Gemini and returns a generated response.

Example response:

```json
{
  "reply": "LLM observability helps monitor and understand the behaviour and performance of language model applications."
}
```

The actual response will vary depending on the model output.

## Step 7: Inspect the Trace in Langfuse

1. Sign in to Langfuse and open your project.
2. Open the traces view.
3. Locate the trace corresponding to your chat request.
4. Open the trace and inspect its observations.
5. Verify that the following stages appear:

   - `chat-request`
   - `validate-input`
   - `retrieve-context`
   - `gemini-generation`
   - `format-response`

6. Open the `gemini-generation` observation and inspect the model input, output, and timing information.

The trace helps you understand how a single request moves through the application and which stages contribute to its execution time.

## Expected Result

By the end of this demo, you should have:

- A working Flask application that calls Gemini.
- Unit tests that pass without requiring real Gemini requests.
- Langfuse traces containing named observations.
- Visibility into the LLM generation stage and the overall request flow.

## Important Notes

- The retrieval stage is simulated; this demo does not connect to a vector database.
- `DEMO_SLOW_REQUEST` is included for the next demo. Setting it to `true` introduces a controlled delay in the generation stage.
- Trace inputs and outputs may contain sensitive information. Use test data and avoid submitting personal or confidential information.
- Token usage and cost reporting depend on the availability of Gemini usage metadata and correct model pricing configuration in Langfuse.

## Cleanup

Stop the application using `Ctrl+C` in the terminal where it is running.

Keep your `.env` file private and retain your environment setup if you plan to continue with Demo 2.