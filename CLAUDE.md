# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Travel Agent — a travel planning chatbot built with LangGraph, LangChain, and Streamlit. It finds flights and hotels via SerpAPI, manages GitHub gists/issues via PyGithub, orchestrates multi-step conversations with human-in-the-loop approval, and sends formatted HTML emails via SendGrid.

## Setup and Running

```bash
# Install dependencies (requires Poetry and Python 3.11+)
pyenv local 3.11.9
poetry install --sync
poetry shell

# Run the app
streamlit run app.py
```

No test framework, linter, or CI/CD pipeline is configured.

## Environment Variables

Create a `.env` file in the project root. Required: `OPENAI_API_KEY`, `SERPAPI_API_KEY`, `SENDGRID_API_KEY`. Optional: `GITHUB_TOKEN` (for gist/issue/repo-search tools), `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT`. The app sets `FROM_EMAIL`, `TO_EMAIL`, `EMAIL_SUBJECT` at runtime from user input.

## Architecture

### Agent Graph (agents/agent.py)

LangGraph `StateGraph` with state `AgentState(TypedDict)` containing `messages: Annotated[list[AnyMessage], operator.add]`.

**Nodes:**
1. `call_tools_llm` — GPT-4o with tool-calling; entry point. System prompt in `TOOLS_SYSTEM_PROMPT`.
2. `invoke_tools` — Executes whichever tool the LLM selected from `TOOLS` list.
3. `email_sender` — Separate GPT-4o call (low temperature) converts conversation to HTML email, sends via SendGrid. Has `interrupt_before` for human-in-the-loop approval.

**Edges:** Conditional from `call_tools_llm`: if tool calls exist -> `invoke_tools` -> loops back to `call_tools_llm`; if no tool calls -> `email_sender` -> END. Memory via `MemorySaver` checkpointer.

### Tools (agents/tools/)

Each tool follows the same pattern: Pydantic v1 input model (`from langchain.pydantic_v1 import BaseModel`), a wrapper schema class with a `params` field, and `@tool(args_schema=...)` decorator. All tools are registered in the `TOOLS` list in `agents/agent.py`.

- `flights_finder.py` — SerpAPI Google Flights engine search
- `hotels_finder.py` — SerpAPI Google Hotels engine search (returns top 5 results)
- `github_plugin.py` — Three tools: `github_create_gist`, `github_create_issue`, `github_search_repos` (PyGithub)

### Streamlit UI (app.py)

Single-page app. `Agent` is initialized once in `st.session_state`. User submits a travel query, agent runs with a new `thread_id`, results display inline. Optional email form resumes the interrupted graph to send email.

## Code Conventions

- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- `dotenv` loaded at module level in `agents/agent.py`
- Tools return error strings on failure (try/except pattern)
- Inline pylint disable directives used; no formatter or linter configured
- Tool input schemas use Pydantic v1 via `langchain.pydantic_v1`, not `pydantic` directly

## Common Tasks

- **Add a new tool**: Create a file in `agents/tools/`, define Pydantic v1 input schema + wrapper schema, add `@tool(args_schema=...)` function, register in `TOOLS` list in `agents/agent.py`, and update `TOOLS_SYSTEM_PROMPT` if the LLM needs guidance on when to use it.
- **Modify agent behavior**: Edit `TOOLS_SYSTEM_PROMPT` or `EMAILS_SYSTEM_PROMPT` in `agents/agent.py`, or restructure the graph nodes/edges.
- **Change the UI**: Edit `app.py` — Streamlit components, session state, form handling.
