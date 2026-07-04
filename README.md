# DocLens — Source-Cited Document Q&A Engine

## 🎯 What This Is
DocLens is a focused, ship ready RAG (Retrieval Augmented Generation) backend that lets a user upload documents (PDF/DOCX, including scanned files) and ask questions in plain language getting back accurate answers with **exact page-level citations**.


---

## 🏗️ Phase 1 — MVP (Build This First, Ship It)

**Goal:** A working RAG pipeline you can demo live in a proposal call or Loom video within 1–2 weeks.

### Core Pipeline
1. **Document Ingestion**
   - Accepts PDF and DOCX uploads
   - OCR fallback for scanned/image-based PDFs (Tesseract or PaddleOCR)
   - Structure-preserving extraction — keep headings, page numbers, and section boundaries intact (don't just flatten to raw text)

2. **Chunking & Indexing**
   - Chunk by semantic/structural boundaries (not fixed character counts) with page-number metadata attached to every chunk
   - Embed chunks into a vector database (ChromaDB — simplest to run locally on your hardware)
   - Hybrid retrieval: vector similarity search + BM25 keyword search, merged/reranked

3. **Query & Citation Engine**
   - User asks a question in plain language
   - Retrieved chunks are passed to an LLM (local via Ollama, quantized model — your RTX 4070 handles 7B-class models comfortably)
   - Answer is generated **with inline citations** that trace back to exact document + page number
   - If the answer isn't supported by retrieved content, the system says so — no hallucinated citations

4. **API Layer**
   - FastAPI backend exposing: `/upload`, `/query`, `/documents` (list/status)
   - Async endpoints so uploads and long document processing don't block
   - Simple auth token so it's not wide open

5. **Demo Interface**
   - Streamlit single-page UI: upload a doc, ask a question, see the answer with clickable/highlighted citations
   - This is what you screen-record for your portfolio and proposals

### Tech Stack (Phase 1)
- **Language:** Python 3.11+
- **API:** FastAPI
- **Retrieval:** ChromaDB + BM25 (rank_bm25 or similar), simple reranker (cross-encoder if time allows)
- **LLM:** Ollama, local quantized model (e.g. Llama 3.1 8B or Mistral 7B, 4-bit)
- **Parsing:** PyMuPDF/pdfplumber for PDFs, python-docx for Word, Tesseract for OCR
- **UI:** Streamlit
- **Containerization:** Single Dockerfile + docker-compose (app + optional local model server)

### Definition of Done for Phase 1
- [ ] Upload a real multi-page PDF (including one scanned page) and it processes without manual cleanup
- [ ] Ask 5 different questions and get answers with correct page citations, verified by hand
- [ ] Ask 1 question with no answer in the document — system correctly says it can't find it
- [ ] Whole thing runs via `docker-compose up` with no manual setup steps
- [ ] 2-minute screen recording showing upload → question → cited answer

---

## 🏗️ Phase 2 — Only After Phase 1 Is Solid and Demoed

**Goal:** Turn the single-agent RAG system into a genuinely agentic, multi-capability system — matching the "RAG + Multi-Agent" and "Text-to-SQL" job posts you're seeing.

### Additions
1. **Text-to-SQL Agent**
   - Given a mock relational database (a few related tables — invoices, customers, orders is enough), translate natural language into SQL
   - Validate generated SQL against schema before execution (defensive check — reuse the validation pattern from your ScriptNet Edu project)
   - Return results in plain language, not raw rows

2. **LangGraph Router**
   - A lightweight routing layer that decides: is this question about *documents* (→ RAG agent) or *data* (→ SQL agent)?
   - This is what makes it legitimately "agentic" rather than a single pipeline — and it's the part that shows up explicitly in job post language ("multi-agent orchestration layer")

3. **Guardrail Circuit**
   - Intercepts LLM output before it reaches the user
   - For SQL: blocks anything that isn't a SELECT, checks table/column names exist
   - For RAG: blocks answers with no supporting citation

### Tech Additions (Phase 2)
- **Orchestration:** LangGraph
- **Database:** SQLite (zero-setup, good enough for a demo schema)
- **Optional:** swap Streamlit for a lightweight React front end if you want the UI to look more "product-grade" for higher-budget proposals

### Definition of Done for Phase 2
- [ ] Ask a document question and a data question in the same session — router sends each to the right agent
- [ ] A deliberately bad SQL request (e.g. "delete all customers") is blocked by the guardrail
- [ ] Updated demo video showing both agent types working

---

## 🚫 Deliberately Cut From the Original Scope (For Now)
These were in the original plan but are cut to keep this finishable. Add them later, per-client, only if a specific job actually asks for them:
- Real multi-tenant data isolation (simulate it in prose in your proposal if a client asks — don't build it speculatively)
- Live streaming inference logs
- Chunked upload infrastructure
- Full dashboard/analytics UI beyond the Streamlit demo

Cutting these isn't giving something up — it's the difference between a project that ships and proves you can deliver, versus one that stays 60% done forever.

---

## 💻 Local Hardware
- Intel Core i7 14th Gen, RTX 4070 (12GB VRAM) — sufficient for 7B-class quantized models via Ollama
- Budget: $0 (fully local execution)

---

