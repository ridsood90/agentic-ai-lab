# Agentic AI Lab

A hands-on project exploring how to design, build, and test agentic AI systems using Python and Large Language Models (LLMs).

The project focuses on understanding the engineering principles behind AI agents rather than simply building applications around LLM APIs.

## Tech Stack

- **Language:** Python
- **LLM:** Qwen3 (8B) via Ollama
- **Data Validation:** Pydantic
- **Persistence:** SQLite
- **Testing:** Python testing with mocked LLM responses

## Current Implementation

### 1. LLM Integration
- Running a locally hosted LLM using Ollama.
- Sending conversational messages to the model.
- Managing LLM context and conversation history.

### 2. Conversation Memory
- Persisting conversation history using SQLite.
- Managing conversation context.
- Implementing conversation summarization to manage context size.

### 3. Structured Output
- Defining structured state using Pydantic.
- Validating state updates returned by the LLM.

### 4. Tool Calling
- Implementing tools for flight and hotel searches.
- Allowing the LLM to invoke tools based on user requests.
- Processing tool results and continuing the conversation.

### 5. Testing
- Using mocked LLM responses for deterministic tests.
- Testing structured output and tool-calling behaviour.
- Exploring dependency injection and test isolation.

### 6. Observability
- Implementing application logging.
- Tracking LLM interactions and tool execution.
- Exploring request-level tracing and execution duration.

## Project Goals

- Understand agentic AI architecture.
- Build reliable LLM-powered applications.
- Explore context management and memory strategies.
- Implement tool orchestration.
- Develop testing and observability practices.
- Learn production engineering principles for AI systems.

## Status

Actively under development. New capabilities and engineering concepts are added incrementally as part of the learning journey.

## Project Structure

agentic-ai-lab/
│
├── src/
│   └── agentic_ai/
│       ├── __init__.py
│       └── config.py
│
├── scripts/
│   ├── hello_llm.py
│   ├── chat_with_memory.py
│   ├── run_travel_agent.py
│   ├── test_agent_mock.py
│   ├── test_context_manager.py
│   ├── test_structured_output.py
│   ├── test_tool_calling.py
│   ├── test_tool_executor.py
│   └── test_tool_retries.py
│
├── tests/
│   └── test_llm_client.py
│
├── requirements.txt
├── .gitignore
└── README.md