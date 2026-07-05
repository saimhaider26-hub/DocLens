# DocLens 📄🔍

**A fully local, multi-agent RAG engine for document and data Q&A — no cloud, no API costs, no data leaving your machine.**

Upload documents, ask questions in plain English, and get answers with exact page-level citations. An intelligent routing layer decides whether your question needs document retrieval or a database query, and dispatches it to the right agent — all running locally via Ollama.

![Status](https://img.shields.io/badge/status-Phase%202%20Complete-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)

---


## ✨ What It Does

- **Upload** PDF documents and ask questions about their content in natural language
- **Get** answers with inline citations tracing back to the exact document and page
- **Query structured data** in plain English — a Text-to-SQL agent translates questions into safe, validated SQL
- **Trust the routing** — a LangGraph-based Supervisor classifies each question (document / data / ambiguous / out-of-scope) and sends it to the correct agent, instead of blindly guessing
- **Trust the guardrails** — if an answer isn't supported by the retrieved context, or a generated SQL query isn't a safe read-only `SELECT`, the system refuses rather than making something up
- **Runs 100% locally** — document processing, embeddings, and LLM inference all happen on your machine via Ollama. Nothing is sent to an external API
- **Secured** — API endpoints require token authentication

---

## 🏗️ Architecture

```
                    ┌─────────────────────┐
                    │   User Question       │
                    └──────────┬────────────┘
                               │
                    ┌──────────▼────────────┐
                    │  Supervisor Router      │
                    │  (LangGraph + LLM)      │
                    │  classifies intent:     │
                    │  document / data /      │
                    │  ambiguous / oos        │
                    └──────┬───────┬──────────┘
                           │       │
              ┌────────────┘       └────────────┐
              ▼                                  ▼
   ┌───────────────────────┐         ┌───────────────────────┐
   │   Document Agent        │        │   Text-to-SQL Agent     │
   │  Hybrid Retrieval:       │       │  NL → SQL generation     │
   │  ChromaDB (vector)       │       │  Guardrail: blocks        │
   │  + BM25 (keyword)         │      │  non-SELECT statements    │
   │  → cited LLM answer       │      │  → executes on SQLite      │
   └───────────────────────┘         └───────────────────────┘
```

### Document Ingestion Pipeline
```
PDF Upload → Text Extraction (PyMuPDF, OCR fallback via Tesseract)
    → Structural Chunking (page-level metadata preserved)
    → Embedding (all-MiniLM-L6-v2) → ChromaDB + BM25 index
    → Hybrid Retrieval → Ollama (Llama 3.1 8B) → Cited Answer
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| API | FastAPI (token-authenticated) |
| Frontend | Streamlit |
| Orchestration | LangGraph |
| Vector DB | ChromaDB |
| Keyword Search | BM25 |
| Embeddings | all-MiniLM-L6-v2 (ONNX) |
| LLM Inference | Ollama (Llama 3.1 8B, local, quantized) |
| Structured Data | SQLite |
| PDF Parsing | PyMuPDF + Tesseract OCR (scanned page fallback) |
| Containerization | Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- [Ollama](https://ollama.com) installed with the model pulled:
  ```bash
  ollama pull llama3.1
  ```

### Run It

```bash
git clone https://github.com/saimhaider26-hub/DocLens.git
cd DocLens
docker-compose up
```

Open the Streamlit UI (default: `http://localhost:8501`), upload a document, and start asking questions.

---

## 🧭 Example Interactions

**Document question:**
> **Q:** "Which specific IT-related laws are included in the Lecture 2 curriculum?"
>
> **A:** Electronic Transactions Ordinance 2002 [PPIT_REPORT_Final.pdf, Page 5]; PECA 2016 [PPIT_REPORT_Final.pdf, Page 5]; FIA Cybercrime Regulations [PPIT_REPORT_Final.pdf, Page 5]; Data Protection [PPIT_REPORT_Final.pdf, Page 5]; Intellectual Property Laws [PPIT_REPORT_Final.pdf, Page 5]

**Ambiguity guardrail:**
> **Q:** "Who is the group leader for this project?" *(asked with two different projects indexed)*
>
> **A:** Flagged as ambiguous — the Supervisor recognizes multiple distinct projects are indexed and asks for clarification instead of guessing which one "this project" refers to.

**Out-of-scope guardrail:**
> **Q:** "What is the capital of Pakistan?"
>
> **A:** Correctly identified as out-of-scope and declined, since it isn't a document or data question relevant to the indexed content.

**Data question (Text-to-SQL):**
> **Q:** "How many customers are in the database?"
>
> **A:** Routed to the SQL agent, which generates and executes a validated `SELECT COUNT(*)` query and returns the result in plain language.

---

## 🔒 Why Local-First Matters

Every step — embedding, retrieval, and generation — runs on your own hardware via Ollama. No document content or database schema ever leaves your machine, there are no per-token API costs, and it works offline once models are pulled. This makes it a realistic foundation for privacy-sensitive use cases: legal documents, internal reports, healthcare records, or any business data that shouldn't touch a third-party LLM API.

---

## ⚠️ Known Limitations

- **Diagrams and visual content:** Text extraction flattens 2D layouts (flowcharts, UML diagrams, architecture diagrams) into linear text, which can scramble spatial relationships between labels. The system handles prose, tables, and scanned text well, but doesn't yet "understand" diagram structure the way a human reading the image would. A multimodal/vision-model extension would be needed to properly interpret diagram content — this is flagged as a scoped Phase 3 candidate, not a current feature.
- **SQL agent works against a demo schema:** the Text-to-SQL agent is built and validated against a sample SQLite schema; connecting it to a production database would need schema-specific tuning.

---

## 🗺️ Roadmap

- [x] **Phase 1** — Core RAG pipeline: ingestion (with OCR fallback), hybrid retrieval, citation-aware generation, hallucination guardrails, FastAPI + Streamlit, full Docker containerization, token-based API auth
- [x] **Phase 2** — Agentic architecture: LangGraph Supervisor routing layer (document / data / ambiguous / out-of-scope classification), Text-to-SQL agent with defensive SQL validation guardrails
- [ ] **Phase 3 (proposed)** — Multimodal extension for diagram/image understanding within documents

---

## 📄 License

MIT

---

## 👤 Author

**Saim Haider**
[GitHub](https://github.com/saimhaider26-hub)
