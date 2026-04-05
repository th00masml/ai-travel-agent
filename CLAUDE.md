# CLAUDE.md

## Project Overview

AI Travel Agent — a travel planning chatbot built with **LangGraph**, **LangChain**, and **Streamlit**. It finds flights and hotels via SerpAPI, orchestrates multi-step conversations with human-in-the-loop approval, and sends formatted HTML emails via SendGrid.

## Repository Structure

```
ai-travel-agent/
├── app.py                    # Streamlit UI and main entry point
├── agents/
│   ├── agent.py              # LangGraph agent logic (state graph, nodes, edges)
│   └── tools/
│       ├── flights_finder.py # Flight search tool (SerpAPI Google Flights)
│       └── hotels_finder.py  # Hotel search tool (SerpAPI Google Hotels)
├── pyproject.toml            # Poetry config and dependencies
├── poetry.lock               # Locked dependency versions
└── __init__.py               # Package marker (empty)
```

## Tech Stack

- **Python** ^3.11
- **LangGraph** ^0.2.0 — state-based agent orchestration
- **LangChain** ^0.2.0 + **langchain-openai** ^0.1.0 — LLM framework
- **Streamlit** ^1.38.0 — web UI
- **SerpAPI** ^0.1.5 — Google Flights/Hotels data
- **SendGrid** ^6.11.0 — email delivery
- **python-dotenv** ^1.0.1 — environment variable loading

## Setup and Running

```bash
# Install dependencies (requires Poetry)
pyenv local 3.11.9
poetry install --sync
poetry shell

# Run the app
streamlit run app.py
```

## Environment Variables

**Required:**
| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT models |
| `SERPAPI_API_KEY` | SerpAPI key for flight/hotel searches |
| `SENDGRID_API_KEY` | SendGrid API key for email delivery |

**Optional (LangChain tracing):**
| Variable | Purpose |
|---|---|
| `LANGCHAIN_API_KEY` | LangChain observability |
| `LANGCHAIN_TRACING_V2` | Set to `true` to enable tracing |
| `LANGCHAIN_PROJECT` | Project name (default: `ai_travel_agent`) |

**Set at runtime by the app:** `FROM_EMAIL`, `TO_EMAIL`, `EMAIL_SUBJECT`

## Architecture

### Agent Graph Flow

1. **`call_tools_llm`** — Invokes GPT-4o with tool-calling to determine next action
2. **`invoke_tools`** — Executes the selected tool (flights or hotels search)
3. **`call_emails_llm`** — Generates HTML email content using GPT-4o (lower temperature)
4. **`email_sender`** — Sends email via SendGrid (has `interrupt_before` for human approval)

Conditional edges route between tool invocation and email generation based on LLM output.

### Key Patterns

- **State management**: `AgentState(TypedDict)` with `Annotated[list[AnyMessage], operator.add]`
- **Human-in-the-loop**: `interrupt_before=['email_sender']` pauses for user confirmation
- **Memory**: `MemorySaver` checkpointer for stateful multi-turn conversations
- **Tool definitions**: `@tool(args_schema=...)` decorator with Pydantic v1 input models
- **Dual LLM configs**: Tool-calling LLM vs email-generation LLM (different temperatures)

## Code Conventions

- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- **Imports**: `dotenv` loaded at module level; LangChain ecosystem imports grouped together
- **Error handling**: try/except with `st.error()` for UI feedback; tools return error strings on failure
- **Pylint**: Some pylint disable directives used inline (`# pylint: disable = ...`)
- **No formatter or linter config**: No Black, Ruff, mypy, or similar tools configured

## Testing

No test framework or test files are currently configured. No CI/CD pipelines exist.

## Common Tasks

- **Add a new tool**: Create a file in `agents/tools/`, define a Pydantic input schema and a `@tool`-decorated function, then register it in the `TOOLS` list in `agents/agent.py`
- **Modify agent behavior**: Edit the system prompts (`TOOLS_SYSTEM_PROMPT`, `EMAILS_SYSTEM_PROMPT`) or the graph structure in `agents/agent.py`
- **Change the UI**: Edit `app.py` (Streamlit components, session state, form handling)
