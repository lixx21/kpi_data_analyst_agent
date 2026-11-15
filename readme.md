# KPI Data Analyst Agent

A multi-step LLM agent workflow that answers procurement KPI questions from a database. Ask a question in plain English, and the agent plans the analysis, writes its own SQL, interprets the results and produces a Markdown report.

Built with **LangGraph**, **Ollama (local models)**, **Streamlit** and **Docker**.

> **Status: v1.** The core workflow runs end to end. It has no accuracy evaluation yet, so treat its answers as drafts to verify.

![Demo](/image/app_result.png)

## What it does

Example question:

> Which supplier has the highest defect rate in Raw Materials?

The agent then:

1. **Plans**: forms one testable hypothesis and breaks the analysis into small steps.
2. **Queries**: writes and runs SQL for each step against the procurement database.
3. **Analyzes**: interprets the query results against the hypothesis.
4. **Reports**: writes a Markdown report with the findings.

The Streamlit UI shows each agent finishing live, then displays the final report.

## Architecture

![architecture](/image/architecture.png)

All agents share one state object (`question`, `plan`, `sql_data`, `analysis`, `report`). Each node reads what it needs from the state and returns only what it produced.

| Node | Model | Job |
|---|---|---|
| Planner | `llama3.2` | Produces a structured `Plan` (hypothesis, assumptions, reasoning, steps) |
| Data Agent | `qwen2.5-coder` | Turns each plan step into SQL and runs it |
| Analyst | `llama3.2` | Interprets the results against the hypothesis |
| Writer | `llama3.2` | Writes the final Markdown report |

## Tech stack

- **Orchestration:** LangGraph, LangChain
- **LLMs:** Ollama, running locally (`llama3.2`, `qwen2.5-coder`), so no data leaves your machine and there are no API costs
- **Data:** SQL database with a `procurement_kpi` table (sample data)
- **Structured output:** Pydantic models
- **UI:** Streamlit
- **Packaging:** Docker Compose

## Getting Started
### Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.11+ (or Docker)

### Pull the models

```bash
ollama pull llama3.2
ollama pull qwen2.5-coder
```

### Run locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

### Run with Docker

<!-- TODO: confirm the Ollama setup in your compose file -->
```bash
docker compose up --build
```

Then open <http://localhost:8501>.

## Limitations

Being upfront about what v1 does not do yet:

- **No accuracy evaluation yet.** There is no benchmark, so I make no accuracy claims.
- **Small local models make mistakes.** For example, the planner sometimes proposes a wrong defect-rate formula (counting rows instead of summing defective units). Always check the SQL and the numbers.
- **Linear workflow.** The agents run in a fixed order (planner → data → analyst → writer). There is no critic or retry loop, so a bad query is not corrected automatically.
- **Single table.** The agent is built around one `procurement_kpi` table.
- **Not production-ready.** This is a portfolio project for learning and demonstration.

## Roadmap

- [ ] Evaluation set (20 to 30 questions with known answers) and model comparison
- [ ] Critic node with a capped retry loop
- [ ] SQL error recovery (send errors back to the SQL writer)
- [ ] SQL guardrails: SELECT-only validation, table allowlist, row limits
- [ ] RAG over the data dictionary and other documents
- [ ] Tracing with Langfuse
- [ ] Multiple tables and richer analysis (statistical tests, charts)

## Author

**Felix**, data analytics engineer