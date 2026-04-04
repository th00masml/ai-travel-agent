# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Running

```bash
# Install dependencies
poetry install --sync
poetry shell

# Run the app
streamlit run app.py
```

**Required `.env` variables:**
```
OPENAI_API_KEY=
SERPAPI_API_KEY=
SENDGRID_API_KEY=
```

Optional LangSmith tracing: `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_PROJECT`.

No linting, formatting, or test commands are configured in this project.

## Architecture

This is a **LangGraph-based travel agent** with a Streamlit UI. The agent searches for flights/hotels via SerpAPI and optionally emails an itinerary via SendGrid.

### Data Flow

1. User submits a query in `app.py` → sent as `HumanMessage` to the LangGraph agent
2. `call_tools_llm` node invokes GPT-4o with bound tools
3. `invoke_tools` node executes flight/hotel search tools, adding `ToolMessage` results
4. Steps 2–3 loop until the LLM makes no more tool calls
5. Execution **interrupts before** `email_sender` — the Streamlit UI resumes the graph only if the user opts in
6. `email_sender` uses a separate GPT-4o call (temperature=0.1) to convert results to HTML, then sends via SendGrid

### Key Files

- **`agents/agent.py`** — LangGraph graph definition, all nodes, system prompts, and the `MemorySaver` checkpointer. The graph is compiled with `interrupt_before=["email_sender"]`.
- **`agents/tools/flights_finder.py`** and **`hotels_finder.py`** — `@tool`-decorated functions with Pydantic input schemas for SerpAPI calls.
- **`app.py`** — Streamlit UI; manages session state (`thread_id` UUID per session), invokes the graph, and handles the email form.

### State & Session Management

- LangGraph state is `TypedDict` with `messages: Annotated[list, operator.add]` for message accumulation.
- Each Streamlit session gets a unique `thread_id`; passed as `{'configurable': {'thread_id': thread_id}}` on every graph invocation.
- `MemorySaver` checkpointer persists state across the interrupt boundary between the search and email steps.

### Multi-Model Pattern

- Tool-calling nodes use GPT-4o with `.bind_tools(tools)`
- Email generation uses a separate `ChatOpenAI(temperature=0.1)` instance with a detailed HTML-formatting system prompt
