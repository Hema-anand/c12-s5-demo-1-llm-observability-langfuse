# Sprint 5: Instrument LLM Observability with Langfuse

# Demo 1: Instrument an LLM-Calling Agent with Langfuse

## Overview

In this demo, you will integrate Google Gemini with a Flask application and use Langfuse to observe how an LLM request is processed.

You will instrument the application with named observations, generate traces, and inspect the execution flow in Langfuse. The application uses a simulated retrieval stage to demonstrate trace analysis without requiring a vector database.

The Gemini generation observation records the complete prompt sent to the model, the model's response, and available token-usage metadata. Langfuse records generation timing automatically. Cost visibility depends on whether Langfuse can calculate cost for the selected model.

## Learning Outcomes

By completing this demo, you will be able to:

- Integrate a Gemini model into a Python application.
- Instrument an LLM application using Langfuse.
- Capture traces with named observations for individual processing stages.
- Inspect LLM inputs, outputs, and execution flow in Langfuse.
- Inspect token usage and verify whether cost information is available.

## Application Flow

A request to the `/chat` endpoint passes through the following stages:

1. **Validate Input:** Check whether the user message is valid.
2. **Retrieve Context:** Simulate a retrieval stage.
3. **Generate Response:** Send the prompt and simulated context to Gemini.
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
GEMINI_MODEL=gemini-3.5-flash-lite

LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_BASE_URL=https://cloud.langfuse.com

APP_VERSION=local
```

Replace the placeholder values with your actual credentials. Use the Langfuse base URL appropriate for your project region if it differs from the example. The model name must be a model supported by your Gemini API account.

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

Verify that all tests pass. The tests should use mocked Gemini responses so they do not need to make actual LLM API calls.

## Step 4: Start the Application

Start the application using Waitress:

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

The application builds a prompt containing instructions, simulated context, and the user's question. It sends that complete prompt to Gemini and returns the generated response.

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
5. Verify that the following observations appear:
   - `chat-request`
   - `validate-input`
   - `retrieve-context`
   - `gemini-generation`
   - `format-response`
6. Open `gemini-generation` and inspect the model input, output, timing, and token-usage details when available.
7. Check whether Langfuse displays cost for the generation.

The trace helps you understand how a single request moves through the application and which stages contribute to its execution time.

## What to Verify for LO1

LO1: **Instrument an LLM-calling agent with Langfuse so every call is captured as a trace (prompt, completion, latency, tokens, cost).**

| Requirement | What to verify in Langfuse |
|---|---|
| Trace the LLM call | The `gemini-generation` observation appears under the request trace. |
| Prompt | The input contains the complete prompt actually sent to Gemini. |
| Completion | The output contains Gemini's returned text. |
| Latency | The generation observation shows its duration. |
| Token usage | Input, output, and total token counts appear when Gemini returns usage metadata and the SDK records it successfully. |
| Cost | Cost is displayed if Langfuse has the required usage data and model-pricing information. |

Token usage and cost are not the same. If usage is missing, check the Gemini response's usage metadata and the installed SDK versions. If cost is missing, check the selected model's pricing configuration and Langfuse's support for that model. Do not report cost as captured unless it is visible or otherwise explicitly recorded.

## Expected Result

By the end of this demo, you should have:

- A working Flask application that calls Gemini.
- Unit tests that pass without requiring real Gemini requests.
- Langfuse traces containing named observations.
- Visibility into the complete prompt, model output, generation timing, and available token-usage information.
- Verified whether cost information is available for the configured model.

## Important Notes

- The retrieval stage is simulated; this demo does not connect to a vector database.
- The application currently makes one Gemini generation call per valid `/chat` request. Each such call is instrumented as a Langfuse generation observation.
- Trace inputs and outputs may contain sensitive information. Use test data and avoid submitting personal or confidential information.
- Token usage depends on the usage metadata returned by Gemini. Cost reporting depends on model pricing and the usage information available to Langfuse.
- The example `.env` model name must match a model supported by your Gemini API account.

## Cleanup

Stop the application using `Ctrl+C` in the terminal where it is running.

Keep your `.env` file private and retain your environment setup if you plan to continue with Demo 2.