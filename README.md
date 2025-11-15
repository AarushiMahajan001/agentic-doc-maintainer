# Agentic Documentation & Code Maintainer

An **agentic AI system** that reads real codebases, discovers important functions, writes API-style documentation, and then **auto-evaluates** that documentation using LLM-as-a-judge.

This project is designed as an **industry-style agentic AI project**: multiple agents, tool-calling, FAISS-based code search, and structured evaluation — all wired together in a small, reproducible Python repo.

---

## ✨ What this project does

Given a Python codebase (local or from GitHub), this system can:

- 🔎 **Search code intelligently** using embeddings + FAISS
- 🧠 **Generate documentation** for key functions/classes via Groq-hosted LLMs
- 🧪 **Evaluate docs automatically** on:
  - correctness
  - coverage
  - clarity
  - consistency with the source code
- 📝 **Write Markdown docs to disk** (one `.md` per module)
- 🧵 Run as a **pipeline** you can reuse on any repo or local project

This is meant to look like the kind of internal tool a company might build for:

- Developer productivity / DevEx
- Keeping code and docs in sync
- Bootstrapping API docs on legacy repos

---

## 🧩 High-level architecture

Core pieces:

- `app/models.py`  
  Pydantic models for:
  - `CodeChunk` (function-level code segments)
  - `DocTaskState` (shared state passed across agents)

- `scripts/ingest_repo.py`  
  Walks `data/repo/`, extracts Python functions, embeds them with a `SentenceTransformer`, and builds a FAISS index:
  - `data/index/code.index`
  - `data/index/metadata.json`

- `app/tools/code_search.py`  
  Loads the FAISS index and metadata and exposes:
  - `search_code(query, top_k)` → list of `CodeChunk`s

- `app/tools/doc_writer.py`  
  Uses Groq LLMs to generate:
  - function-level documentation
  - a final module-level Markdown page

- `app/agents/*.py`  
  Agents over the shared state:
  - `planner_agent.py` → `plan_doc_task(state)`
  - `code_search_agent.py` → `run_code_search_agent(state)`
  - `doc_writer_agent.py` → `run_doc_writer_agent(state)`
  - `evaluator_agent.py` → `run_evaluator_agent(state)` (LLM-as-judge)

- `app/orchestration/graph.py`  
  A simple orchestration function:
  - `run_documentation_pipeline(module_path, query=None)`  
    → runs planner → search → doc writer → evaluator → final doc assembly → writes `.md`.

- `scripts/run_cli_demo.py`  
  CLI entrypoint to run the full pipeline on a specific module and print:
  - final Markdown docs
  - evaluation scores

---

## ⚙️ Setup

### 1. Clone this repo

```bash
git clone https://github.com/AarushiMahajan001/agentic-doc-maintainer.git
cd agentic-doc-maintainer
