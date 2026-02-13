# CLAUDE.md

## Project Overview

AI Travel Agent is a LangGraph-based travel planning assistant. It uses OpenAI GPT-4o to understand user travel requests, searches for flights and hotels via SerpAPI (Google Flights & Google Hotels), presents results through a Streamlit web UI, and can send formatted HTML travel summaries via SendGrid email. The agent supports human-in-the-loop review before sending emails.

## Tech Stack

- **Language**: Python ^3.11
- **Package Manager**: Poetry (`pyproject.toml` + `poetry.lock`)
- **Agent Framework**: LangGraph ^0.2.0 / LangChain ^0.2.0
- **LLM**: OpenAI GPT-4o (via `langchain-openai`)
- **Search APIs**: SerpAPI (Google Flights engine, Google Hotels engine)
- **Email**: SendGrid ^6.11.0
- **Web UI**: Streamlit ^1.38.0
- **Env Management**: python-dotenv

## Project Structure

```
ai-travel-agent/
├── app.py                          # Streamlit web UI entry point
├── __init__.py                     # Package init (empty)
├── agents/
│   ├── __init__.py                 # Package init (empty)
│   ├── agent.py                    # LangGraph agent: state graph, LLM bindings, system prompts
│   └── tools/
│       ├── __init__.py             # Package init (empty)
│       ├── flights_finder.py       # @tool for Google Flights search via SerpAPI
│       └── hotels_finder.py        # @tool for Google Hotels search via SerpAPI
├── pyproject.toml                  # Poetry dependencies and project metadata
├── poetry.lock                     # Locked dependency versions
├── .gitignore                      # Standard Python gitignore
├── LICENSE                         # MIT License
└── README.md                       # User-facing documentation
```

## Architecture

The agent uses a LangGraph `StateGraph` with this flow:

```
call_tools_llm  ──(has tool_calls?)──→  invoke_tools  ──→  call_tools_llm (loop)
      │
      └──(no tool_calls)──→  email_sender  ──→  END
```

Key architectural details:

- **AgentState**: A `TypedDict` with a single `messages` field using `Annotated[list[AnyMessage], operator.add]` for message accumulation.
- **Two LLM instances**: `_tools_llm` (GPT-4o with tools bound) for travel queries, and a separate `email_llm` (GPT-4o, temperature=0.1) for precise HTML email formatting.
- **Human-in-the-loop**: The graph compiles with `interrupt_before=['email_sender']`, pausing execution before sending email so users can review.
- **State persistence**: `MemorySaver()` provides in-memory checkpointing (state is lost on restart).
- **Conditional routing**: `exists_action()` checks if the last message has `tool_calls` to decide between looping back to tools or proceeding to email.

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI: initializes agent, handles user queries, renders results, provides email form. Uses `st.session_state` for agent and thread persistence across rerenders. |
| `agents/agent.py` | Core `Agent` class: builds the LangGraph `StateGraph`, defines `call_tools_llm`, `invoke_tools`, and `email_sender` nodes, contains system prompts (`TOOLS_SYSTEM_PROMPT`, `EMAILS_SYSTEM_PROMPT`). |
| `agents/tools/flights_finder.py` | `flights_finder` tool: Pydantic schema (`FlightsInput`) for parameters (airports, dates, passengers, stops). Calls SerpAPI `google_flights` engine. Returns `best_flights` results. |
| `agents/tools/hotels_finder.py` | `hotels_finder` tool: Pydantic schema (`HotelsInput`) for parameters (location, dates, guests, rooms, hotel class). Calls SerpAPI `google_hotels` engine. Returns top 5 properties sorted by rating. |

## Setup & Running

```bash
# Install dependencies
poetry install --sync

# Activate virtual environment
poetry shell

# Run the application
streamlit run app.py
```

### Required Environment Variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=<your_key>
SERPAPI_API_KEY=<your_key>
SENDGRID_API_KEY=<your_key>

# Optional: LangChain observability
LANGCHAIN_API_KEY=<your_key>
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai_travel_agent
```

Email-related env vars (`FROM_EMAIL`, `TO_EMAIL`, `EMAIL_SUBJECT`) are set dynamically at runtime via the Streamlit email form.

## Development Conventions

- **No test suite**: No tests, pytest config, or CI/CD pipeline exist. Testing is manual via the Streamlit UI.
- **No linter/formatter config**: No pyproject.toml sections for ruff, black, flake8, etc. Selective `# pylint: disable` comments are used in source files.
- **Pydantic v1 compatibility**: Tools use `from langchain.pydantic_v1 import BaseModel, Field` (not standard pydantic) for LangChain tool schema compatibility.
- **Environment variables**: Loaded at module level via `load_dotenv()` in `agents/agent.py`. API keys accessed with `os.environ.get()`.
- **Error handling in tools**: `flights_finder` wraps SerpAPI calls in try/except and returns error strings back to the LLM so it can retry. `hotels_finder` does not have this wrapping.
- **Tool schema pattern**: Each tool defines a `*Input` model for parameters and a `*InputSchema` wrapper model with a `params` field, passed via `@tool(args_schema=...)`.

## Common Patterns

- **LangChain `@tool` decorator**: All tools use `@tool(args_schema=SchemaClass)` with explicit Pydantic input schemas.
- **Optional fields with defaults**: Tool input models use `Optional[type] = Field(default, description=...)` extensively.
- **Streamlit session state**: `st.session_state` stores the `Agent` instance, `thread_id`, and `travel_info` across UI rerenders.
- **UUID thread IDs**: Each query session gets a `uuid.uuid4()` thread ID for LangGraph checkpointing.
- **Dual LLM pattern**: Tools LLM has higher temperature and tools bound; email LLM has low temperature (0.1) for deterministic HTML output.

## Important Notes

- `app.py:85` contains a hardcoded absolute image path (`/Users/Nir.Bar/...`) for the sidebar image. This will fail on any other machine.
- All state is in-memory via `MemorySaver` — restarting the app loses all conversation history.
- No database is used anywhere in the project.
- The project has no tests, type checking, or CI/CD configuration.
- `langchain.pydantic_v1` is used intentionally — do not migrate to standard pydantic without verifying LangChain tool compatibility.
