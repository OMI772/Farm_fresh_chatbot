# FarmFresh AI Chatbot

An intelligent farming and food assistant built with **Streamlit**, **LangGraph**, and **Ollama**. The chatbot answers general questions via web search and tracks FarmFresh orders using tool-augmented LLM workflows with persistent conversation history in PostgreSQL.

## Features

- **Conversational UI** — Streamlit chat interface with multi-thread support
- **Agentic workflow** — LangGraph state machine with conditional tool routing
- **Web search** — DuckDuckGo integration for up-to-date answers
- **Order tracking** — Mock order status lookup (FF1001, FF1002, FF1003)
- **Persistent memory** — Conversation checkpoints stored in PostgreSQL
- **Optional tracing** — LangSmith integration for observability

## How it works

This project combines an LLM agent, a LangGraph workflow, tool calling, and PostgreSQL-backed persistence.

### LangGraph workflow

The agent is built as a **state machine** in `graph/workflow.py`:

```
START → generate_response → [tools_condition] → tools → generate_response → END
                              ↓ (no tool call)
                             END
```

- **`generate_response`** — Calls the Ollama LLM (`llama3.2`) with the current message history.
- **`tools`** — Runs any tool the model requested (search, order lookup).
- **`tools_condition`** — LangGraph’s built-in router that sends the flow to `tools` when the LLM returns tool calls, otherwise ends the turn.

Conversation state is defined in `graph/state.py` as a `ChatState` with a `messages` list. New messages are merged in via LangGraph’s `add_messages` reducer.

### Tool calling

The LLM is **tool-augmented** in `graph/nodes.py`:

- `ChatOllama` is bound to tools with `model.bind_tools(TOOL_LIST)`.
- When the model needs live data, it returns structured **tool calls** instead of a plain text answer.
- `ToolNode` executes those calls and appends **tool results** back into state.
- The graph loops to `generate_response` so the model can read tool output and reply in natural language.

| Tool | File | Purpose |
|---|---|---|
| `search_on_duckduckgo` | `graph/tools.py` | Web search via DuckDuckGo (`ddgs`) for up-to-date answers |
| `get_order_tracking` | `graph/tools.py` | Mock FarmFresh order status lookup (`mock/mock_order_api.py`) |

Example flow for *“Track order FF1001”*:

1. User message is added to state.
2. LLM decides to call `get_order_tracking(order_id="FF1001")`.
3. Tool node runs the mock API and returns status JSON.
4. LLM generates a final assistant message using that result.

### PostgreSQL checkpointer

Conversation history is persisted with **LangGraph’s `PostgresSaver`** (`graph/workflow.py`):

- Each chat thread uses a unique `thread_id` (UUID).
- After every graph step, LangGraph saves a **checkpoint** to PostgreSQL.
- `checkpointer.setup()` creates the required tables on startup.
- The Streamlit sidebar loads past threads via `ThreadService`, which lists `thread_id`s from the checkpointer.
- Switching threads calls `workflow.get_state()` to restore the full message history.

This gives the chatbot **durable memory** across app restarts without custom session storage.

### PostgreSQL connection

Database access is handled in `dao/db_conn.py`:

- Reads `DATABASE_URL` from `.env` (see `config/settings.py`).
- Creates a **`psycopg` connection pool** (`min_size=1`, `max_size=5`).
- Pool settings: `autocommit=True`, `dict_row` factory for LangGraph compatibility.
- The same pool is passed to `PostgresSaver`, so checkpoint reads/writes reuse pooled connections.

**Example connection string:**

```
DATABASE_URL=postgresql://farmfresh_app:your_password@localhost:5432/farmfresh
```

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Streamlit  │────▶│  LangGraph       │────▶│  Ollama         │
│  (app.py)   │     │  Workflow        │     │  (llama3.2)     │
└─────────────┘     └────────┬─────────┘     └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌──────────────┐
        │ DuckDuck │  │ Order API │  │ PostgreSQL   │
        │ Go Search│  │ (mock)    │  │ Checkpointer │
        └──────────┘  └───────────┘  └──────────────┘
```

### Project structure

```
Farm_fresh_chatbot/
├── app.py                  # Streamlit entry point
├── assets/
│   └── styles.css          # Custom UI theme
├── config/
│   └── settings.py         # Environment configuration
├── dao/
│   └── db_conn.py          # PostgreSQL connection pool
├── graph/
│   ├── nodes.py            # LLM and tool nodes
│   ├── state.py            # LangGraph state schema
│   ├── tools.py            # Agent tools (search, order tracking)
│   └── workflow.py         # Graph definition and compilation
├── mock/
│   └── mock_order_api.py   # Mock order status data
├── services/
│   └── thread_service.py   # Conversation thread management
├── tests/
│   └── test_graph.py       # Workflow smoke tests
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/) with the `llama3.2` model pulled
- PostgreSQL 14+

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repository-url>
cd Farm_fresh_chatbot

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the Ollama model

```bash
ollama pull llama3.2
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `LANGCHAIN_API_KEY` | Optional — LangSmith API key |
| `LANGCHAIN_PROJECT` | Optional — LangSmith project name |
| `LANGCHAIN_TRACING_V2` | Optional — set to `true` to enable tracing |

**Example PostgreSQL setup:**

```sql
CREATE DATABASE farmfresh;
CREATE USER farmfresh_app WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE farmfresh TO farmfresh_app;
```

### 5. Run the application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage examples

| Prompt | Behavior |
|---|---|
| *What is crop rotation?* | General answer via LLM |
| *Latest news on organic farming* | Web search via DuckDuckGo |
| *Track order FF1001* | Order status lookup tool |

## Development

### Run tests

```bash
pip install pytest
pytest tests/ -v
```

### Mock order IDs

| Order ID | Status |
|---|---|
| `FF1001` | Out for delivery |
| `FF1002` | Delivered |
| `FF1003` | Processing |

## Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Orchestration | LangGraph (`StateGraph`, conditional edges) |
| LLM | Ollama (`llama3.2`) with tool binding |
| Tools | LangChain `@tool` + `ToolNode` (DuckDuckGo, order tracking) |
| Persistence | PostgreSQL + `PostgresSaver` checkpointer |
| Database client | `psycopg` connection pool |
| Observability | LangSmith (optional) |

## License

MIT
