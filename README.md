# ScholarFlow AI

A backend Retrieval-Augmented Generation (RAG) system for document question-answering, built with FastAPI. Upload documents, index them into a vector database, and ask natural-language questions answered using retrieved context from the source material.

The system is built around a **provider-factory architecture** — the LLM backend and vector database are swappable through configuration rather than code changes — and is fully containerized with a production-style observability stack (Prometheus + Grafana) alongside the application.

---

## Features

- **Document ingestion pipeline** — PDF parsing via [Docling](https://github.com/docling-project/docling), with structural understanding of tables, figures, and equations, not just flat text extraction.
- **Context-aware chunking** — uses Docling's `HybridChunker` with heading-aware contextualization, so each chunk carries its section path (e.g. *"Chapter 2 → Methodology"*) alongside the raw text, plus metadata: page numbers, element types, token count, and chunk type (table / figure caption / equation / text).
- **Pluggable LLM backends** — generation and embedding clients are created through a provider factory, currently supporting **Groq** and **Gemini** for generation, and **BGE** for embeddings, selected entirely via environment configuration.
- **Pluggable vector database backends** — supports both **PostgreSQL (pgvector)** and **Qdrant** as interchangeable vector stores, selected via configuration.
- **RAG query pipeline** — indexes document chunks into the configured vector store, retrieves the most relevant chunks for a query, and generates a grounded answer using the retrieved context.
- **Evaluation harness** — an offline evaluation pipeline measuring both retrieval quality (hit rate, MRR against a curated question set) and generation quality (RAGAS-based faithfulness, answer relevancy, context precision/recall).
- **Observability** — Prometheus metrics and Grafana dashboards covering both standard HTTP request metrics and RAG-specific signals (empty-retrieval rate, top-retrieval-score distribution), instrumented directly in the retrieval path.
- **Containerized, multi-service deployment** — Docker Compose orchestrates the API, PostgreSQL/pgvector, Qdrant, an Nginx reverse proxy, Prometheus, Grafana, and metrics exporters for Postgres and system-level stats.

---

## Architecture

```
                        ┌──────────┐
                        │  Nginx   │  (reverse proxy, :80)
                        └────┬─────┘
                             │
                        ┌────▼─────┐
                        │ FastAPI  │  (:8000)
                        └────┬─────┘
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼──────┐
        │ PostgreSQL │  │  Qdrant   │  │  LLM APIs  │
        │ (pgvector) │  │ (vectors) │  │ Groq/Gemini│
        └────────────┘  └───────────┘  └────────────┘

        ┌────────────┐   ┌──────────┐
        │ Prometheus │──▶│ Grafana  │
        └────────────┘   └──────────┘
```

The application layer follows a **controller/router/model** separation:

- **`routers/`** — FastAPI route definitions (`data`, `rag`, `base`), handling request validation and response shaping.
- **`controllers/`** — business logic (`ProcessController` for document parsing/chunking, `RAGController` for indexing/retrieval/generation, `ProjectController`, `DataController`).
- **`models/`** — data access layer for projects, assets, and chunks.
- **`stores/`** — provider implementations behind factory interfaces for LLM clients (`stores/llm/`) and vector database clients (`stores/vector_db/`), so a new backend can be added by implementing the provider interface without touching controller logic.
- **`evaluation/`** — standalone evaluation harness, independent of the running API, for measuring retrieval and generation quality against a golden dataset.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI, Uvicorn |
| Document parsing | Docling (PDF parsing, table/figure structure extraction) |
| Chunking | Docling `HybridChunker` with HuggingFace tokenizer-aware splitting |
| Embeddings | BGE (via `sentence-transformers`) |
| Generation | Groq, Gemini |
| Vector storage | PostgreSQL + pgvector, or Qdrant (configurable) |
| Relational storage | PostgreSQL (SQLAlchemy async ORM, Alembic migrations) |
| Evaluation | RAGAS, custom retrieval metrics |
| Observability | Prometheus, Grafana, `prometheus-client` |
| Containerization | Docker, Docker Compose |
| Reverse proxy | Nginx |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/` | Application status/info |
| `GET` | `/api/health` | Health check |
| `POST` | `/data/upload/{project_id}` | Upload a document to a project |
| `POST` | `/data/process/{project_id}` | Parse and chunk uploaded document(s) into the relational store |
| `POST` | `/api/rag/index/push/{project_id}` | Embed and index a project's chunks into the vector database |
| `GET` | `/api/rag/index/info/{project_id}` | Get vector collection info for a project |
| `POST` | `/api/rag/index/search/{project_id}` | Semantic search over a project's indexed chunks |
| `POST` | `/api/rag/index/answer/{project_id}` | Ask a question, answered using retrieved context |

---

## Getting Started

### Prerequisites
- Docker and Docker Compose
- API keys for your chosen LLM provider (Groq and/or Gemini)

### Setup

```bash
git clone https://github.com/Naden-Mohamed/ScholarFlow-AI.git
cd ScholarFlow-AI
```

Create the required environment files under `docker/env/` (see `docker/env/*.env.example` for the expected variables): `.env.app`, `.env.postgres`, `.env.grafana`, `.env.postgres-exporter`.

Key variables in `.env.app`:
```dotenv
POSTGRES_HOST=pgvector          # service name on the Docker network, not localhost
QDRANT_URL=qdrant:6333
VECTOR_DB_BACKEND=PGVECTOR       # or QDRANT
GENERATION_BACKEND=GROQ          # or GEMINI
EMBEDDING_BACKEND=BGE
```

### Run

```bash
docker compose -f docker/docker-compose.yml up --build
```

This builds and starts the full stack. The API is available at `http://localhost:8000` (or via Nginx at `http://localhost/`), Prometheus at `http://localhost:9090`, and Grafana at `http://localhost:3000`.

Database migrations run automatically on container start via the app's entrypoint script before the server starts.

---

## Evaluation

The `src/evaluation/` module provides an offline harness for measuring RAG quality independent of the running API:

- **Retrieval metrics** (`evaluation/metrics/retrieval_metrics.py`) — hit rate and MRR computed against a curated question set (`evaluation/testset/qa_pairs.json`).
- **Generation metrics** (`evaluation/metrics/generation_metrics.py`) — RAGAS-based faithfulness, answer relevancy, context precision, and context recall.

Run it with:
```bash
python -m evaluation.run_eval
```

---

## Monitoring

Beyond standard HTTP request count/latency metrics, the application exposes RAG-specific Prometheus metrics instrumented directly in the retrieval path:

- `rag_empty_retrieval_total` — counts queries that returned no retrieved documents.
- `rag_top_retrieval_score` — histogram of the top retrieved chunk's similarity score per query.

These are scraped by Prometheus and can be visualized in Grafana alongside system-level metrics from `node-exporter` and `postgres-exporter`.

---

## Project Structure

```
ScholarFlow-AI/
├── docker/
│   ├── docker-compose.yml
│   ├── scholarflow/          # FastAPI Dockerfile + entrypoint
│   ├── nginx/
│   └── prometheus/
├── src/
│   ├── main.py                # App entrypoint, lifespan-managed client setup
│   ├── controllers/           # Business logic
│   ├── routers/                # API route definitions
│   ├── models/                 # Data access layer
│   │   └── db_schemas/scholarflow/  # SQLAlchemy models + Alembic migrations
│   ├── stores/
│   │   ├── llm/                # LLM provider factory + implementations
│   │   └── vector_db/          # Vector DB provider factory + implementations
│   ├── evaluation/             # Retrieval/generation evaluation harness
│   ├── utils/                  # Prometheus metrics setup
│   └── helpers/                # Config, client bootstrap
└── README.md
```

---

## Roadmap

Features under active development, not yet implemented:

- Hybrid retrieval (dense + BM25) with cross-encoder reranking
- Cross-document comparison and structured multi-paper analysis
- Section-aware retrieval filtering (chunk metadata already captures section headings; filtering by section is not yet exposed via the API)
- Citation-grounded generation with explicit source attribution in responses
- CI/CD pipeline (automated linting, testing, and evaluation gating on pull requests)

---

## License

MIT License
