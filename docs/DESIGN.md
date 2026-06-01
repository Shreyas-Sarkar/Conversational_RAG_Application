# DESIGN.md
# Conversational RAG Platform — Architecture & Design Specification

**Version:** 1.0.0
**Status:** Approved for Implementation
**Audience:** Engineering, Architecture Review

---

## Table of Contents

1. Architectural Goals
2. Architectural Constraints
3. Technology Selection Analysis
   - 3.1 Vector Database Comparison
   - 3.2 Groq Model Comparison
   - 3.3 Deployment Platform Comparison
4. Final Technology Decisions
5. System Architecture
   - 5.1 High-Level Architecture
   - 5.2 Component Diagram
   - 5.3 Data Flow Diagram
6. Sequence Diagrams
   - 6.1 PDF Ingestion Flow
   - 6.2 Embedding Flow
   - 6.3 Query and Retrieval Flow
   - 6.4 Citation Generation Flow
   - 6.5 Chat and Conversation Memory Flow
   - 6.6 Document Management Flow
7. API Architecture
   - 7.1 Endpoint Specifications
   - 7.2 Request Schemas
   - 7.3 Response Schemas
   - 7.4 Error Schema
8. Frontend Architecture
9. Backend Architecture
10. Service Layer Design
11. Storage Design
    - 11.1 Metadata Schema
    - 11.2 Vector Schema
    - 11.3 Conversation History Schema
12. Folder Structure
13. State Management Strategy
14. Configuration Management
15. Security Design
16. Logging Design
17. Monitoring Design
18. Deployment Architecture
19. Design Tradeoffs
20. Future Extension Points

---

## 1. Architectural Goals

The following architectural goals drive all design decisions in this document. Every technology choice, component boundary, and data flow is evaluated against these goals.

**AG-01: Simplicity First**
Every component must be as simple as it can be while still meeting requirements. Complexity is introduced only when simplicity would violate a requirement.

**AG-02: Modularity**
Components must be independently replaceable. Swapping the vector database, LLM provider, or frontend framework must require changes only in the integration layer, not in business logic.

**AG-03: Traceability**
Every design decision must map to a requirement in REQUIREMENTS.md. Untraceable decisions are a signal of overengineering.

**AG-04: Zero Cost**
The architecture must operate entirely within free-tier limits of all services. No design decision may require a paid service.

**AG-05: Portfolio Clarity**
The architecture must be legible to a senior engineer reviewing it as a portfolio artifact. It must demonstrate real architectural thinking, not just working code.

**AG-06: Beginner Friendliness**
A developer with 6 months of Python experience must be able to understand and implement any component by reading the code and docstrings.

---

## 2. Architectural Constraints

The following constraints are non-negotiable. They are enforced by project requirements and cannot be relaxed.

| ID | Constraint | Source |
|----|------------|--------|
| AC-01 | Frontend must be Streamlit | Project Requirements |
| AC-02 | Backend must be FastAPI | Project Requirements |
| AC-03 | Embeddings must use Sentence Transformers | Project Requirements |
| AC-04 | LLM inference must use Groq API | Project Requirements |
| AC-05 | All services must operate within free-tier limits | NFR-07 |
| AC-06 | Frontend and backend must be independently deployable | DR-03 |
| AC-07 | No secrets may be committed to version control | SR-01 |
| AC-08 | The application must be publicly accessible after deployment | DR-01, DR-02 |

---

## 3. Technology Selection Analysis

### 3.1 Vector Database Comparison

Five vector database candidates were evaluated. The evaluation criteria are weighted by their importance to this project's constraints and goals.

#### Evaluation Criteria and Weights

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Free-tier sustainability | 25% | Critical — project must operate at zero cost indefinitely |
| Ease of deployment | 20% | High — must be usable by a single developer without DevOps expertise |
| Learning curve | 15% | High — beginner-friendliness is an explicit architectural goal |
| Production readiness | 10% | Medium — portfolio must demonstrate real engineering |
| Developer experience | 10% | Medium — affects implementation speed and maintainability |
| Resume/portfolio value | 10% | Medium — employer recognizability matters for this use case |
| Scalability headroom | 5% | Low — not required for this scope |
| Community adoption | 5% | Low — affects longevity and documentation quality |

#### Candidate Evaluation

**Pinecone**

Pinecone is a managed, fully hosted vector database with a generous free tier ("Starter" plan). It provides a cloud-native REST API, no local infrastructure, and excellent documentation.

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| Free-tier sustainability | 3 | Free tier exists but is limited to 1 index, ~100k vectors; no guaranteed permanence |
| Ease of deployment | 5 | Fully managed; zero infrastructure to run |
| Learning curve | 4 | Simple Python SDK; well-documented |
| Production readiness | 5 | Industry standard; battle-tested |
| Developer experience | 4 | Excellent SDK; clear error messages |
| Resume/portfolio value | 5 | Highly recognizable; frequently mentioned in job descriptions |
| Scalability | 5 | Scales infinitely with paid tiers |
| Community | 5 | Large community; extensive tutorials |
| **Weighted Score** | **3.85** | |

Tradeoffs: Strong resume value and ease of use, but the free tier has changed multiple times and free-tier index capacity is limited. External dependency adds a network call for every write and query, increasing latency. Free tier cannot be guaranteed to remain unchanged.

**Qdrant**

Qdrant is an open-source vector search engine that can be run locally or deployed as a managed cloud service. Its cloud offering has a free tier ("Free Cluster").

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| Free-tier sustainability | 4 | Free cloud cluster; also runnable locally with zero cost |
| Ease of deployment | 4 | Local: run via Docker or pip; Cloud: managed |
| Learning curve | 3 | Python SDK is good; slightly more concepts to learn |
| Production readiness | 4 | Production-grade; actively developed |
| Developer experience | 4 | Good SDK; REST and gRPC interfaces |
| Resume/portfolio value | 4 | Growing recognition; modern choice |
| Scalability | 4 | Good scaling story on paid tiers |
| Community | 3 | Smaller but growing community |
| **Weighted Score** | **3.80** | |

Tradeoffs: Excellent local-first story (no cloud dependency for development). Cloud free tier is limited. Running locally is ideal for development but introduces complexity in deployment (either a second service, or switching to cloud for production).

**ChromaDB**

ChromaDB is an open-source, embedded vector database designed specifically for AI applications. It runs in-process with no external service required.

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| Free-tier sustainability | 5 | Fully in-process; zero external cost |
| Ease of deployment | 5 | pip install; runs in the same process as FastAPI |
| Learning curve | 5 | Simplest API of all candidates |
| Production readiness | 3 | Maturing; persistence backend improved in 0.4+ |
| Developer experience | 5 | Pythonic API; minimal boilerplate |
| Resume/portfolio value | 3 | Known in AI circles but less enterprise recognition |
| Scalability | 2 | Limited; designed for single-process use |
| Community | 4 | Large AI community adoption |
| **Weighted Score** | **4.20** | |

Tradeoffs: Best fit for this project's constraints. Runs in-process means no external service dependency, zero latency overhead, and no free-tier limitations. The main weakness is scalability, which is irrelevant for this scope. Production readiness concerns are acceptable given the portfolio use case.

**pgvector**

pgvector is a PostgreSQL extension that adds vector similarity search. It requires a PostgreSQL instance.

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| Free-tier sustainability | 3 | Requires PostgreSQL; free-tier Postgres options exist (Neon, Supabase) but add complexity |
| Ease of deployment | 2 | Requires PostgreSQL setup, extension installation, schema creation |
| Learning curve | 3 | Familiar SQL syntax but requires understanding vector types |
| Production readiness | 5 | PostgreSQL is battle-tested; excellent for hybrid queries |
| Developer experience | 3 | SQL is familiar but vector-specific operations are verbose |
| Resume/portfolio value | 4 | Strong; demonstrates SQL + AI knowledge |
| Scalability | 4 | PostgreSQL scales well with proper indexing |
| Community | 4 | PostgreSQL community is massive |
| **Weighted Score** | **3.10** | |

Tradeoffs: Best production readiness but worst ease of deployment. Adding a PostgreSQL dependency increases infrastructure complexity. For a single-developer portfolio project with zero-cost requirements, this introduces unnecessary operational overhead.

**Weaviate**

Weaviate is an open-source, cloud-native vector database with a managed cloud offering (WCS) that includes a free sandbox.

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| Free-tier sustainability | 3 | Free sandbox exists but expires after a period; not guaranteed permanent |
| Ease of deployment | 3 | Cloud: managed; local: Docker required |
| Learning curve | 2 | Complex schema definition; GraphQL query language |
| Production readiness | 5 | Enterprise-grade; widely used |
| Developer experience | 3 | Schema-first design adds friction for quick projects |
| Resume/portfolio value | 4 | Good enterprise recognition |
| Scalability | 5 | Excellent horizontal scaling |
| Community | 3 | Moderate community |
| **Weighted Score** | **3.15** | |

Tradeoffs: Strong production credibility but high learning curve and a GraphQL API that adds complexity. The free sandbox expiration is a real risk for a portfolio application expected to be demo-able indefinitely.

#### Summary Comparison Table

| Database | Free-Tier | Deployment | Learning Curve | Prod Ready | DX | Portfolio Value | Scalability | Community | **Weighted Score** |
|----------|-----------|------------|----------------|------------|----|-----------------|-------------|-----------|-------------------|
| Pinecone | 3 | 5 | 4 | 5 | 4 | 5 | 5 | 5 | **3.85** |
| Qdrant | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | **3.80** |
| **ChromaDB** | **5** | **5** | **5** | **3** | **5** | **3** | **2** | **4** | **4.20** |
| pgvector | 3 | 2 | 3 | 5 | 3 | 4 | 4 | 4 | **3.10** |
| Weaviate | 3 | 3 | 2 | 5 | 3 | 4 | 5 | 3 | **3.15** |

#### Decision: ChromaDB

**Selected:** ChromaDB (in-process, ephemeral per-session with in-memory mode for demos; persistent mode optional for local development)

**Primary Justification:**
ChromaDB's in-process architecture is the only option that fully satisfies AC-05 (zero cost), AC-06 (independent deployability), and AG-01 (simplicity) simultaneously. Every alternative either introduces an external service dependency, a temporary free tier, or significant operational complexity.

**Specific Reasons Alternatives Were Rejected:**
- **Pinecone:** Free tier is externally managed and has changed before; adds network latency; requires API key management for a second external service
- **Qdrant:** Excellent alternative, but cloud free tier limitations and local Docker requirement for production increase deployment complexity beyond what this scope requires
- **pgvector:** Requires a separate PostgreSQL instance; increases infrastructure surface area; complexity penalty not justified by the scalability benefit
- **Weaviate:** GraphQL learning curve is unnecessary for this scope; free sandbox expiration poses a demo longevity risk

**ChromaDB Configuration for This Project:**
- Use `chromadb.Client()` (ephemeral/in-memory) for simplicity and zero-persistence-overhead
- Session isolation is achieved via collection naming with a session UUID prefix
- Collections are deleted when a user clears their session
- For local development with larger documents, `chromadb.PersistentClient(path="./chroma_store")` can be substituted without code changes

---

### 3.2 Groq Model Comparison

Groq provides ultra-low-latency LLM inference through their LPU hardware. Models available on the free tier were evaluated for this RAG use case.

#### Evaluation Criteria

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| RAG suitability (instruction following) | 30% | Must accurately follow "answer only from context" instructions |
| Context window | 25% | Larger window allows more retrieved chunks in the prompt |
| Free-tier availability | 20% | Must be available on the Groq free tier |
| Latency (TTFT) | 15% | Lower latency improves streaming UX |
| Response quality | 10% | Overall answer quality for document Q&A tasks |

#### Candidate Models

**llama-3.3-70b-versatile**
- Parameters: 70B
- Context window: 128,000 tokens
- Free tier: Yes
- Strengths: Excellent instruction following, large context window ideal for multi-chunk RAG, high-quality reasoning
- Weaknesses: Higher latency than smaller models due to parameter count; may hit free-tier token limits faster under heavy use

**llama-3.1-8b-instant**
- Parameters: 8B
- Context window: 128,000 tokens
- Free tier: Yes
- Strengths: Extremely low latency, same large context window, sufficient quality for RAG tasks
- Weaknesses: Less reliable instruction following than 70B for complex multi-hop reasoning; occasionally fails to stay within provided context

**gemma2-9b-it**
- Parameters: 9B
- Context window: 8,192 tokens
- Free tier: Yes
- Strengths: Good instruction following, low latency
- Weaknesses: 8K context window is severely limiting for multi-chunk RAG prompts; eliminated for context window size alone

**mixtral-8x7b-32768**
- Parameters: Mixture of Experts (~13B active)
- Context window: 32,768 tokens
- Free tier: Yes
- Strengths: Good reasoning quality, moderate latency
- Weaknesses: Smaller context window than Llama 3.x models; model has been superseded by newer options

#### Model Selection Summary

| Model | RAG Suitability | Context Window | Free Tier | Latency | Quality | **Weighted Score** |
|-------|----------------|----------------|-----------|---------|---------|-------------------|
| **llama-3.3-70b-versatile** | 5 | 5 | 5 | 3 | 5 | **4.60** |
| llama-3.1-8b-instant | 4 | 5 | 5 | 5 | 3 | **4.40** |
| gemma2-9b-it | 3 | 1 | 5 | 5 | 3 | **3.05** |
| mixtral-8x7b-32768 | 4 | 3 | 5 | 4 | 4 | **3.90** |

#### Decision: Primary and Fallback Models

**Primary Model:** `llama-3.3-70b-versatile`

Justification: Highest RAG suitability score and a 128K context window that enables injecting up to 20+ retrieved chunks per query without context pressure. Groq's LPU hardware mitigates the latency penalty of 70B parameters — the TTFT on Groq is competitive with smaller models on GPU inference. Instruction-following quality is critical for a RAG system that must refuse to answer outside its context.

**Fallback Model:** `llama-3.1-8b-instant`

Justification: Same context window, extremely low latency, and acceptable quality for straightforward document Q&A. Used when the primary model is rate-limited or temporarily unavailable.

**Model String Constants:**
```
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"
```

---

### 3.3 Deployment Platform Comparison

Frontend and backend must be deployed independently to free-tier platforms that provide public HTTPS URLs.

#### Backend Deployment Candidates

**Render (Free Tier)**
- Type: Platform-as-a-Service
- Free tier: Web services with 512 MB RAM, 0.1 CPU; spins down after 15 minutes of inactivity
- Build: Automatic from GitHub; Dockerfile or pip requirements
- Cold start: 30–60 seconds after spin-down
- Custom domain: Yes
- Environment variables: Yes, via dashboard
- Pros: Simple git-push deployment, HTTPS auto-provisioned, FastAPI/uvicorn well-supported, large community documentation
- Cons: Spin-down on inactivity causes cold-start delays; 512 MB RAM may be insufficient for Sentence Transformer model in memory simultaneously with the vector store

**Railway (Legacy Free Tier)**
- As of 2024, Railway no longer offers a meaningfully free tier for production deployments. It has a limited trial credit model. Eliminated.

**Fly.io (Free Tier)**
- Type: Container-based PaaS
- Free tier: 3 shared CPU VMs, 256 MB RAM each; no automatic spin-down
- Build: Docker-based
- Cold start: Minimal (always-on within free tier)
- Pros: No cold-start delays, Docker-based deployment is flexible, always-on within free tier
- Cons: Requires Dockerfile; 256 MB RAM is very tight for Sentence Transformer + ChromaDB + FastAPI; requires Fly CLI for deployment

**Hugging Face Spaces (as backend)**
- Type: ML app hosting
- Free tier: CPU-only, 16 GB RAM (generous), no spin-down
- Build: Docker or Gradio/Streamlit native
- Pros: 16 GB RAM is ample for Sentence Transformer model; no spin-down; direct environment variable support
- Cons: Primarily designed for ML demos; FastAPI requires Docker Space setup; slightly more complex CI

#### Frontend Deployment Candidates

**Streamlit Community Cloud**
- Type: Managed Streamlit hosting
- Free tier: Unlimited public apps from public GitHub repos
- Build: Automatic from GitHub main branch
- Pros: Zero-configuration Streamlit deployment; 1-click from GitHub; secrets management built in; directly supports Streamlit apps
- Cons: GitHub repository must be public; 1 GB RAM limit; no custom domains on free tier

**Hugging Face Spaces (Streamlit)**
- Type: ML app hosting
- Free tier: CPU-only Streamlit Spaces with 16 GB RAM
- Build: Streamlit native
- Pros: Generous RAM; Hugging Face is well-known to ML employers; can host both frontend and backend in one Space
- Cons: Builds can be slower; somewhat less discoverable than direct Streamlit Community Cloud for Streamlit apps

#### Deployment Decision

**Backend: Render**

Justification: Render's free tier is the most straightforward path to a publicly accessible FastAPI service with git-push deployment. The cold-start issue is documented and acceptable for a portfolio application. The RAM limitation (512 MB) is addressed by using the Sentence Transformer model with lazy loading and ChromaDB in-memory mode — both are lightweight enough to coexist within 512 MB.

Assumption: `all-MiniLM-L6-v2` model is approximately 80 MB on disk and ~120 MB in memory. ChromaDB in-memory mode adds minimal overhead. FastAPI + uvicorn add ~50 MB. Total estimated memory: ~280 MB, within the 512 MB limit with headroom.

Cold-start mitigation: A simple ping service or a note in the README advising users to allow 30–60 seconds on first load.

**Frontend: Streamlit Community Cloud**

Justification: Zero-configuration deployment for Streamlit applications directly from a public GitHub repository. This is the canonical Streamlit deployment path, is well-documented, and requires no Docker knowledge. Streamlit Community Cloud provides secrets management for the backend URL configuration.

**Alternative considered:** Hosting both on Hugging Face Spaces would provide more RAM but adds deployment complexity and is not the canonical path for Streamlit apps. The Render + Streamlit Community Cloud combination is simpler and better-documented.

---

## 4. Final Technology Decisions

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Frontend | Streamlit | ≥ 1.35 | Required; supports st.chat_message, st.chat_input, session_state |
| Backend | FastAPI | ≥ 0.111 | Required; async support, automatic OpenAPI, CORS middleware |
| ASGI Server | Uvicorn | ≥ 0.29 | Standard FastAPI production server |
| PDF Extraction | PyMuPDF (fitz) | ≥ 1.24 | Fast, accurate, preserves page metadata; pure Python install |
| Text Chunking | LangChain TextSplitter | ≥ 0.2 | RecursiveCharacterTextSplitter; well-tested, configurable |
| Embeddings | sentence-transformers | ≥ 2.7 | Required; all-MiniLM-L6-v2 model |
| Vector Database | ChromaDB | ≥ 0.5 | Selected per analysis above |
| LLM Provider | Groq SDK | ≥ 0.8 | Required; llama-3.3-70b-versatile primary |
| HTTP Client | httpx | ≥ 0.27 | Async HTTP client for Streamlit → FastAPI calls |
| Configuration | python-dotenv | ≥ 1.0 | Environment variable loading |
| Backend Deployment | Render | N/A | Selected per analysis above |
| Frontend Deployment | Streamlit Community Cloud | N/A | Selected per analysis above |

**Embedding Model:** `all-MiniLM-L6-v2`
- Dimensions: 384
- Max sequence length: 256 tokens
- Disk size: ~80 MB
- Memory footprint: ~120 MB
- Quality: Excellent for semantic similarity tasks
- License: Apache 2.0

**Chunk Configuration:**
- Chunk size: 500 characters
- Chunk overlap: 50 characters
- Splitter: RecursiveCharacterTextSplitter (splits on paragraph → sentence → word boundaries)

Justification: 500-character chunks are small enough to be specific (avoiding noise in retrieval) and large enough to contain a complete thought. 50-character overlap preserves context across chunk boundaries without excessive redundancy. These values are configurable via environment variables.

**Retrieval Configuration:**
- Top-K: 5 chunks per query
- Similarity metric: Cosine similarity (ChromaDB default)

Justification: 5 chunks provide enough context for most document Q&A tasks without overwhelming the prompt. At ~500 characters per chunk, 5 chunks contribute ~2,500 characters (~625 tokens) to the prompt — well within the 128K context window.

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Browser                              │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Streamlit Community Cloud                              │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Streamlit Application                        │ │
│  │                                                                │ │
│  │  ┌──────────────┐  ┌────────────────┐  ┌───────────────────┐ │ │
│  │  │  Upload UI   │  │   Chat UI      │  │  Document Panel   │ │ │
│  │  │  Component   │  │   Component    │  │  Component        │ │ │
│  │  └──────┬───────┘  └──────┬─────────┘  └─────────┬─────────┘ │ │
│  │         │                 │                        │           │ │
│  │         └─────────────────┼────────────────────────┘           │ │
│  │                           │                                    │ │
│  │                  ┌────────▼────────┐                           │ │
│  │                  │  API Client     │  (httpx)                  │ │
│  │                  │  Layer          │                           │ │
│  │                  └────────┬────────┘                           │ │
│  └───────────────────────────┼────────────────────────────────────┘ │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTPS REST / SSE
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Render (Free Tier)                           │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Application                         │ │
│  │                                                                │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
│  │  │  Ingest     │  │  Query       │  │  Document            │ │ │
│  │  │  Router     │  │  Router      │  │  Management Router   │ │ │
│  │  └──────┬──────┘  └──────┬───────┘  └────────┬─────────────┘ │ │
│  │         │                │                    │               │ │
│  │         └────────────────┼────────────────────┘               │ │
│  │                          │                                    │ │
│  │              ┌───────────┼───────────────┐                   │ │
│  │              │           │               │                   │ │
│  │     ┌────────▼───┐  ┌────▼──────┐  ┌────▼──────┐            │ │
│  │     │  Ingestion │  │ Retrieval │  │    RAG    │            │ │
│  │     │  Service   │  │ Service   │  │ Orchestr. │            │ │
│  │     └────────┬───┘  └────┬──────┘  └────┬──────┘            │ │
│  │              │           │               │                   │ │
│  │     ┌────────▼───┐  ┌────▼──────┐  ┌────▼──────┐            │ │
│  │     │  PDF       │  │ Embedding │  │  Groq     │            │ │
│  │     │  Processor │  │ Service   │  │  Client   │            │ │
│  │     └────────────┘  └────┬──────┘  └───────────┘            │ │
│  │                          │                                   │ │
│  │                  ┌───────▼────────┐                          │ │
│  │                  │  ChromaDB      │  (in-process)            │ │
│  │                  │  (In-Memory)   │                          │ │
│  │                  └────────────────┘                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               │ HTTPS
                               ▼
              ┌────────────────────────────────┐
              │       Groq API                 │
              │   llama-3.3-70b-versatile      │
              └────────────────────────────────┘
```

### 5.2 Component Diagram

```
Backend Components:
─────────────────

┌──────────────────────────────────────────────────────┐
│  api/                                                │
│  ├── routers/                                        │
│  │   ├── ingest.py        ← /api/v1/documents/*      │
│  │   ├── query.py         ← /api/v1/query/*          │
│  │   └── documents.py     ← /api/v1/documents (GET, DELETE) │
│  └── main.py              ← FastAPI app, CORS, health │
│                                                      │
│  services/                                           │
│  ├── pdf_processor.py     ← PyMuPDF text extraction  │
│  ├── chunker.py           ← LangChain text splitting  │
│  ├── embedding_service.py ← SentenceTransformer       │
│  ├── vector_store.py      ← ChromaDB operations       │
│  ├── retrieval_service.py ← Query embedding + search  │
│  ├── llm_client.py        ← Groq API + streaming      │
│  └── rag_orchestrator.py  ← Prompt assembly + chain   │
│                                                      │
│  models/                                             │
│  ├── schemas.py           ← Pydantic request/response │
│  └── metadata.py          ← Document, chunk metadata  │
│                                                      │
│  config/                                             │
│  └── settings.py          ← pydantic-settings config  │
└──────────────────────────────────────────────────────┘

Frontend Components:
────────────────────

┌──────────────────────────────────────────────────────┐
│  frontend/                                           │
│  ├── app.py               ← Streamlit entry point    │
│  ├── components/                                     │
│  │   ├── upload.py        ← Upload zone + progress   │
│  │   ├── chat.py          ← Chat messages + input    │
│  │   ├── citations.py     ← Citation cards/expanders │
│  │   ├── document_panel.py← Document list + remove   │
│  │   └── theme_toggle.py  ← Dark/light toggle        │
│  ├── api_client.py        ← httpx wrapper for backend│
│  ├── state.py             ← Session state management │
│  └── styles/                                         │
│      └── neo_brutalist.py ← CSS injection + theme    │
└──────────────────────────────────────────────────────┘
```

### 5.3 Data Flow Diagram

```
PDF Upload and Ingestion Data Flow:
────────────────────────────────────

  [PDF File]
      │
      ▼ (multipart/form-data)
  [FastAPI /api/v1/documents/upload]
      │
      ▼
  [pdf_processor.py]
  extract_text_by_page()
  → List[PageContent(page_num, text)]
      │
      ▼
  [chunker.py]
  split_pages_into_chunks()
  → List[Chunk(chunk_id, doc_id, doc_name, page_num, text)]
      │
      ▼
  [embedding_service.py]
  generate_embeddings(texts)
  → List[np.ndarray] (384-dim vectors)
      │
      ▼
  [vector_store.py]
  upsert_chunks(chunks, embeddings, session_id)
  → Stored in ChromaDB collection
      │
      ▼
  [metadata stored in session state]
  DocumentMetadata(doc_id, filename, page_count, chunk_count, timestamp)
      │
      ▼
  [HTTP 200 → UploadResponse]
  {document_id, filename, page_count, chunk_count}


Query and Response Data Flow:
──────────────────────────────

  [User Query String]
      │
      ▼ (JSON POST)
  [FastAPI /api/v1/query/chat]
      │
      ▼
  [embedding_service.py]
  generate_embedding(query)
  → np.ndarray (384-dim vector)
      │
      ▼
  [vector_store.py]
  similarity_search(query_vec, session_id, top_k=5)
  → List[RetrievedChunk(chunk_id, doc_name, page_num, text, score)]
      │
      ▼
  [rag_orchestrator.py]
  build_prompt(query, retrieved_chunks, conversation_history)
  → PromptMessages (system + history + user)
      │
      ▼
  [llm_client.py]
  stream_completion(prompt_messages, model)
  → Generator[str]  (streaming tokens)
      │
      ▼
  [FastAPI StreamingResponse]
  → SSE stream to Streamlit frontend
      │
      ▼
  [Streamlit st.write_stream()]
  → Tokens displayed progressively
      │
      ▼ (after stream complete)
  [citations rendered from retrieved_chunks metadata]
```

---

## 6. Sequence Diagrams

### 6.1 PDF Ingestion Flow

```
User         Streamlit        FastAPI        PDFProcessor    Chunker    EmbeddingService    VectorStore
 │               │               │               │              │              │                │
 │──upload PDF──▶│               │               │              │              │                │
 │               │──POST /upload▶│               │              │              │                │
 │               │               │──extract()───▶│              │              │                │
 │               │               │               │──pages[]────▶│              │                │
 │               │               │               │              │──split()────▶│                │
 │               │               │               │              │              │──embed()        │
 │               │               │               │              │              │──vectors[]     │
 │               │               │               │              │              │                │
 │               │               │◀──────────────────────────────────────────────upsert()──────▶│
 │               │               │                                                              │
 │               │◀──200 UploadResponse─────────────────────────────────────────────────────────│
 │◀──success UI──│               │               │              │              │                │
```

### 6.2 Query and Retrieval Flow

```
User         Streamlit        FastAPI        EmbeddingService    VectorStore    RAGOrchestrator    LLMClient    Groq API
 │               │               │               │                   │               │               │              │
 │──type query──▶│               │               │                   │               │               │              │
 │               │──POST /chat──▶│               │                   │               │               │              │
 │               │               │──embed query─▶│                   │               │               │              │
 │               │               │◀──query vec───│                   │               │               │              │
 │               │               │──search()────────────────────────▶│               │               │              │
 │               │               │◀──top-K chunks────────────────────│               │               │              │
 │               │               │──build_prompt()──────────────────────────────────▶│               │              │
 │               │               │◀──prompt_messages─────────────────────────────────│               │              │
 │               │               │──stream_completion()──────────────────────────────────────────────▶│             │
 │               │               │                                                                   │──API call───▶│
 │               │               │                                                                   │◀──stream─────│
 │               │◀──SSE tokens──│               │                   │               │               │              │
 │◀──text stream─│               │               │                   │               │               │              │
 │               │               │                                                              (stream ends)        │
 │◀──citations───│               │               │                   │               │               │              │
```

### 6.3 Citation Generation Flow

```
Retrieved Chunks (from VectorStore):
  [
    {chunk_id: "c1", doc_name: "report.pdf", page_num: 3, text: "..."},
    {chunk_id: "c2", doc_name: "summary.pdf", page_num: 7, text: "..."},
    ...
  ]

Citation Assembly (in rag_orchestrator.py):
  1. Deduplicate chunks by (doc_name, page_num)
  2. Sort citations by document name, then page number
  3. Format: [{source: "report.pdf", page: 3, excerpt: "...first 200 chars..."}, ...]

Citation Display (in frontend/components/citations.py):
  For each citation:
    st.expander(f"📄 {source} — Page {page}")
      └── st.caption(excerpt)
```

### 6.4 Conversation Memory Flow

```
Session State: st.session_state.messages = []

Turn 1:
  User: "What is the main finding?"
  System: appends {role: "user", content: "...", timestamp: "..."}
  LLM: responds
  System: appends {role: "assistant", content: "...", sources: [...], timestamp: "..."}

Turn 2:
  User: "Can you elaborate on that?"
  System: builds prompt with history:
    [
      {role: "system", content: RAG_SYSTEM_PROMPT + context_chunks},
      {role: "user",   content: "What is the main finding?"},        ← Turn 1
      {role: "assistant", content: "The main finding is..."},         ← Turn 1
      {role: "user",   content: "Can you elaborate on that?"}        ← Turn 2 (current)
    ]

History Truncation (when history > MAX_HISTORY_TURNS):
  - Keep last N turns (default: 10 turns = 20 messages)
  - Always keep the current user message
  - Emit a warning log if truncation occurs
```

### 6.5 Document Management Flow

```
Document Add:
  upload → process → store in vector_store → update session_state.documents dict

Document Remove:
  user clicks remove → confirm dialog → 
  DELETE /api/v1/documents/{doc_id}?session_id={session_id} →
  vector_store.delete_by_doc_id(doc_id, session_id) →
  remove from session_state.documents

Session Clear:
  user clicks clear → confirm dialog →
  DELETE /api/v1/session/{session_id} →
  vector_store.delete_collection(session_id) →
  clear session_state.documents, session_state.messages
```

---

## 7. API Architecture

### 7.1 Endpoint Specifications

All endpoints are prefixed with `/api/v1`.

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /health | Health check | None |
| POST | /api/v1/documents/upload | Upload and process a PDF | None |
| GET | /api/v1/documents | List documents for a session | None |
| DELETE | /api/v1/documents/{doc_id} | Remove a document from a session | None |
| DELETE | /api/v1/session/{session_id} | Clear all session data | None |
| POST | /api/v1/query/chat | Submit a query and stream a response | None |

Note: No authentication is implemented in this version. Session isolation is achieved via session_id (UUID) generated by the frontend and passed in all requests.

---

#### GET /health

**Purpose:** Deployment health check

**Response:**
```json
{
  "status": "ok",
  "vector_store": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**HTTP Codes:** 200 OK, 503 Service Unavailable (if vector store check fails)

---

#### POST /api/v1/documents/upload

**Purpose:** Upload a PDF, process it, and index its chunks

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | PDF file to upload |
| session_id | string | Yes | UUID identifying the user session |

**Response (200):**
```json
{
  "document_id": "uuid-v4",
  "filename": "report.pdf",
  "page_count": 42,
  "chunk_count": 187,
  "status": "indexed"
}
```

**HTTP Codes:**
- 200: Success
- 400: Invalid file type
- 413: File too large
- 422: Text extraction failed (likely image-only PDF)
- 500: Internal processing error

---

#### GET /api/v1/documents

**Purpose:** List all documents active in a session

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

**Response (200):**
```json
{
  "documents": [
    {
      "document_id": "uuid-v4",
      "filename": "report.pdf",
      "page_count": 42,
      "chunk_count": 187,
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_chunks": 187
}
```

---

#### DELETE /api/v1/documents/{doc_id}

**Purpose:** Remove a document and its vectors from the session

**Path Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| doc_id | string | Yes | Document UUID |

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

**Response (200):**
```json
{
  "deleted": true,
  "document_id": "uuid-v4",
  "chunks_removed": 187
}
```

**HTTP Codes:** 200, 404 (document not found in session)

---

#### DELETE /api/v1/session/{session_id}

**Purpose:** Clear all documents, vectors, and session state

**Path Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

**Response (200):**
```json
{
  "cleared": true,
  "session_id": "uuid-v4",
  "documents_removed": 3,
  "chunks_removed": 512
}
```

---

#### POST /api/v1/query/chat

**Purpose:** Submit a query and receive a streaming response

**Request (JSON):**
```json
{
  "session_id": "uuid-v4",
  "query": "What is the main conclusion of the report?",
  "conversation_history": [
    {"role": "user", "content": "What documents are uploaded?"},
    {"role": "assistant", "content": "You have uploaded report.pdf."}
  ],
  "top_k": 5
}
```

**Response:** `text/event-stream` (Server-Sent Events)

Stream format:
```
data: {"type": "token", "content": "The"}
data: {"type": "token", "content": " main"}
data: {"type": "token", "content": " conclusion"}
...
data: {"type": "sources", "content": [{"doc_name": "report.pdf", "page": 3, "excerpt": "..."}]}
data: {"type": "done"}
```

**HTTP Codes:** 200 (streaming), 404 (no documents in session), 500 (LLM error)

---

### 7.2 Request Schemas (Pydantic)

```python
# models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ConversationMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="UUID identifying the user session")
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_history: List[ConversationMessage] = Field(default=[])
    top_k: int = Field(default=5, ge=1, le=20)

class DocumentListRequest(BaseModel):
    session_id: str
```

### 7.3 Response Schemas (Pydantic)

```python
class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str  # "indexed"

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_chunks: int

class DeleteDocumentResponse(BaseModel):
    deleted: bool
    document_id: str
    chunks_removed: int

class ClearSessionResponse(BaseModel):
    cleared: bool
    session_id: str
    documents_removed: int
    chunks_removed: int

class HealthResponse(BaseModel):
    status: str
    vector_store: str
    timestamp: datetime

# SSE stream events (serialized to JSON in data field)
class StreamToken(BaseModel):
    type: str = "token"
    content: str

class StreamSources(BaseModel):
    type: str = "sources"
    content: List[dict]  # [{doc_name, page, excerpt}]

class StreamDone(BaseModel):
    type: str = "done"
```

### 7.4 Error Schema

```python
class ErrorResponse(BaseModel):
    error: str          # Machine-readable error code
    message: str        # Human-readable description
    detail: Optional[str] = None  # Additional detail (never a stack trace in production)
    request_id: Optional[str] = None  # For log correlation
```

Example:
```json
{
  "error": "INVALID_FILE_TYPE",
  "message": "Only PDF files are accepted. Please upload a .pdf file.",
  "detail": "Received MIME type: image/png",
  "request_id": "req_abc123"
}
```

---

## 8. Frontend Architecture

The Streamlit frontend is organized as a single-page application with a sidebar and main content area. All state is managed through `st.session_state`.

### Page Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Header: App name + theme toggle                                   │
├─────────────────────┬──────────────────────────────────────────────┤
│  Sidebar            │  Main Content Area                           │
│                     │                                              │
│  Document Panel     │  [If no documents: Upload Zone]              │
│  ─────────────      │                                              │
│  📄 report.pdf      │  [If documents: Chat Interface]              │
│     42 pages        │                                              │
│     187 chunks      │  ┌───────────────────────────────────────┐   │
│     [Remove]        │  │  Chat History                         │   │
│                     │  │  (scrollable)                         │   │
│  📄 summary.pdf     │  │                                       │   │
│     12 pages        │  │  User: What is the main finding?      │   │
│     [Remove]        │  │                                       │   │
│                     │  │  AI: The main finding is...           │   │
│  ──────────────     │  │  ▼ 📄 report.pdf – Page 3            │   │
│  Total: 2 docs      │  │  ▼ 📄 summary.pdf – Page 7           │   │
│  239 chunks         │  │                                       │   │
│                     │  └───────────────────────────────────────┘   │
│  [Clear Session]    │                                              │
│  [Download Chat]    │  ┌───────────────────────────────────────┐   │
│                     │  │  [Upload Another PDF]                 │   │
│                     │  │                                       │   │
│                     │  │  Ask a question...            [Send]  │   │
│                     │  └───────────────────────────────────────┘   │
└─────────────────────┴──────────────────────────────────────────────┘
```

### State Schema

```python
# state.py — All keys that may exist in st.session_state

SESSION_STATE_SCHEMA = {
    "session_id": str,           # UUID, generated on first load
    "messages": list,            # List of ConversationMessage dicts
    "documents": dict,           # {doc_id: DocumentInfo dict}
    "theme": str,                # "light" | "dark"
    "is_processing": bool,       # True while upload is running
    "is_querying": bool,         # True while LLM is responding
    "last_error": str | None,    # Last error message to display
}
```

### API Client Design

```python
# api_client.py

class RAGAPIClient:
    """
    Thin wrapper around httpx for all backend API calls.
    All methods are async-friendly via asyncio.run() shim for Streamlit.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def upload_document(self, file_bytes: bytes, filename: str, session_id: str) -> UploadResponse: ...
    def list_documents(self, session_id: str) -> DocumentListResponse: ...
    def delete_document(self, doc_id: str, session_id: str) -> DeleteDocumentResponse: ...
    def clear_session(self, session_id: str) -> ClearSessionResponse: ...
    def stream_chat(self, request: ChatRequest) -> Generator[dict, None, None]: ...
```

---

## 9. Backend Architecture

### Service Layer Responsibilities

Each service has a single, well-defined responsibility. Services do not call each other directly; they are composed in the router layer.

| Service | File | Responsibility |
|---------|------|----------------|
| PDFProcessor | services/pdf_processor.py | Extract page-by-page text from a PDF file |
| Chunker | services/chunker.py | Split page text into overlapping chunks with metadata |
| EmbeddingService | services/embedding_service.py | Load the Sentence Transformer model; generate embeddings |
| VectorStore | services/vector_store.py | ChromaDB operations: upsert, search, delete by doc, delete collection |
| RetrievalService | services/retrieval_service.py | Embed query; call VectorStore.search; return RetrievedChunk list |
| LLMClient | services/llm_client.py | Groq API calls; streaming; retry logic; fallback model |
| RAGOrchestrator | services/rag_orchestrator.py | Build prompt from query + context + history; call LLMClient |

### Dependency Injection Pattern

Services with expensive initialization (EmbeddingService, VectorStore) are instantiated once at application startup using FastAPI's dependency injection with `@lru_cache` or application lifespan events.

```python
# main.py

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize shared services
    app.state.embedding_service = EmbeddingService()
    app.state.vector_store = VectorStore()
    yield
    # Shutdown: cleanup
    pass

app = FastAPI(lifespan=lifespan)
```

Services are injected into routers via FastAPI's `Depends()`:

```python
# routers/query.py

def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service

@router.post("/chat")
async def chat(
    body: ChatRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStore = Depends(get_vector_store),
):
    ...
```

### Request Lifecycle

```
HTTP Request arrives
    │
    ▼
FastAPI middleware stack
    │ CORS validation
    │ Request ID injection
    │ Request logging
    ▼
Route handler (router)
    │
    ▼
Input validation (Pydantic)
    │ On failure: 422 Unprocessable Entity
    ▼
Business logic (services)
    │ On failure: caught exception → ErrorResponse
    ▼
Response assembly
    │
    ▼
HTTP Response
    │ On streaming: StreamingResponse with SSE
    ▼
Response logging (status code, duration)
```

---

## 10. Service Layer Design

### PDFProcessor

```
Input:  bytes (PDF file content)
Output: List[PageContent(page_number: int, text: str)]

Steps:
1. Open PDF from bytes using fitz.open()
2. Iterate pages
3. Extract text via page.get_text("text")
4. Skip empty pages
5. Raise ValueError if no text extracted across all pages

Error handling:
- fitz.FileDataError → raise ValueError("Could not parse PDF")
- All pages empty → raise ValueError("PDF contains no extractable text")
```

### Chunker

```
Input:  List[PageContent], doc_id: str, doc_name: str
Output: List[Chunk(chunk_id, doc_id, doc_name, page_number, text, chunk_index)]

Steps:
1. Initialize RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
2. For each PageContent:
   a. Split text into sub-chunks
   b. Assign metadata to each sub-chunk (doc_id, doc_name, page_number, chunk_index)
   c. Assign UUID4 as chunk_id
3. Return flat list of all chunks

Configuration: chunk_size and chunk_overlap are loaded from settings
```

### EmbeddingService

```
Initialization (once at startup):
  Load SentenceTransformer("all-MiniLM-L6-v2")
  Model is cached in memory for the application lifetime

Input (generate_embeddings):  List[str] (chunk texts)
Output:                        List[List[float]] (384-dim vectors)

Steps:
1. Batch encode all texts: model.encode(texts, batch_size=32, show_progress_bar=False)
2. Convert to list of lists
3. Return

Input (generate_embedding):   str (single query text)
Output:                        List[float] (384-dim vector)

Performance: batch encoding is always used for ingestion
```

### VectorStore

```
Initialization (once at startup):
  client = chromadb.Client()  # ephemeral in-memory

Collection naming:
  Each session uses a separate ChromaDB collection: "session_{session_id}"
  This provides isolation between sessions without authentication

upsert_chunks(chunks, embeddings, session_id):
  collection = get_or_create_collection(f"session_{session_id}")
  collection.upsert(
    ids=[chunk.chunk_id for chunk in chunks],
    embeddings=embeddings,
    documents=[chunk.text for chunk in chunks],
    metadatas=[{
      "doc_id": chunk.doc_id,
      "doc_name": chunk.doc_name,
      "page_number": chunk.page_number,
      "chunk_index": chunk.chunk_index
    } for chunk in chunks]
  )

similarity_search(query_embedding, session_id, top_k, doc_ids_filter=None):
  collection = get_collection(f"session_{session_id}")
  where = {"doc_id": {"$in": doc_ids_filter}} if doc_ids_filter else None
  results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    where=where,
    include=["documents", "metadatas", "distances"]
  )
  return List[RetrievedChunk]

delete_by_doc_id(doc_id, session_id):
  collection = get_collection(f"session_{session_id}")
  collection.delete(where={"doc_id": doc_id})

delete_collection(session_id):
  client.delete_collection(f"session_{session_id}")
```

### RAGOrchestrator

```
build_prompt(query, retrieved_chunks, conversation_history):
  
  System message:
    RAG_SYSTEM_PROMPT = """
    You are a helpful document assistant. Answer questions based ONLY on the 
    provided document context. If the answer is not present in the provided 
    context, say: "I cannot find information about this in the uploaded documents."
    
    Do not speculate or use information outside the provided context.
    Always cite the document name and page number when referencing information.
    
    Context from documents:
    {context_block}
    """
    
    context_block = format_chunks_as_context(retrieved_chunks)
    # Format: "--- [report.pdf, Page 3] ---\n{text}\n\n--- [summary.pdf, Page 7] ---\n{text}"
  
  History messages:
    Include last min(len(history), MAX_HISTORY_TURNS * 2) messages
    
  Current user message:
    {"role": "user", "content": query}
  
  Return: List[dict] (OpenAI-compatible message format)
```

### LLMClient

```
stream_completion(messages, model=PRIMARY_MODEL):
  try:
    client = Groq(api_key=settings.GROQ_API_KEY)
    stream = client.chat.completions.create(
      model=model,
      messages=messages,
      stream=True,
      max_tokens=1000,
      temperature=0.1
    )
    for chunk in stream:
      if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
  
  except RateLimitError:
    if model == PRIMARY_MODEL:
      yield from stream_completion(messages, model=FALLBACK_MODEL)
    else:
      raise
  
  except APIError as e:
    if model == PRIMARY_MODEL and e.status_code >= 500:
      yield from stream_completion(messages, model=FALLBACK_MODEL)
    else:
      raise
```

---

## 11. Storage Design

### 11.1 Document Metadata Schema

Stored in the FastAPI application's session-scoped dict (in-memory). Since ChromaDB is also in-memory, all data is ephemeral per server process.

```python
@dataclass
class DocumentMetadata:
    document_id: str       # UUID4
    filename: str          # Original filename
    page_count: int        # Total pages extracted
    chunk_count: int       # Total chunks indexed
    session_id: str        # Parent session UUID
    uploaded_at: datetime  # UTC timestamp
```

### 11.2 Vector Schema (ChromaDB)

ChromaDB stores each chunk as:

```
id:        chunk_id (UUID4 string)
embedding: List[float] (384 dimensions)
document:  chunk_text (raw string)
metadata:  {
    doc_id:       string (UUID4),
    doc_name:     string (filename),
    page_number:  int,
    chunk_index:  int
}
```

Collection name: `session_{session_id}`

### 11.3 Conversation History Schema

Stored in `st.session_state.messages`:

```python
[
    {
        "role": "user",
        "content": "What is the main finding?",
        "timestamp": "2024-01-01T00:00:00Z"
    },
    {
        "role": "assistant",
        "content": "The main finding is...",
        "timestamp": "2024-01-01T00:00:01Z",
        "sources": [
            {
                "doc_name": "report.pdf",
                "page": 3,
                "excerpt": "First 200 characters of the retrieved chunk..."
            }
        ]
    }
]
```

---

## 12. Folder Structure

```
rag-platform/
│
├── backend/
│   ├── main.py                     ← FastAPI app entry point
│   ├── config/
│   │   └── settings.py             ← pydantic-settings BaseSettings class
│   ├── api/
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── ingest.py           ← POST /api/v1/documents/upload
│   │       ├── query.py            ← POST /api/v1/query/chat
│   │       └── documents.py        ← GET/DELETE /api/v1/documents/*
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py
│   │   ├── chunker.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   ├── retrieval_service.py
│   │   ├── llm_client.py
│   │   └── rag_orchestrator.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py              ← Pydantic request/response models
│   │   └── metadata.py             ← Domain dataclasses
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile                    ← For Render: "web: uvicorn main:app --host 0.0.0.0 --port $PORT"
│
├── frontend/
│   ├── app.py                      ← Streamlit entry point
│   ├── api_client.py               ← httpx-based backend client
│   ├── state.py                    ← Session state initialization and helpers
│   ├── components/
│   │   ├── __init__.py
│   │   ├── upload.py               ← Upload zone component
│   │   ├── chat.py                 ← Chat history and input
│   │   ├── citations.py            ← Citation expander cards
│   │   ├── document_panel.py       ← Sidebar document list
│   │   └── theme_toggle.py         ← Dark/light toggle
│   ├── styles/
│   │   └── neo_brutalist.py        ← CSS injection via st.markdown
│   ├── requirements.txt
│   ├── .env.example
│   └── .streamlit/
│       └── config.toml             ← Streamlit theme base settings
│
├── tests/
│   ├── backend/
│   │   ├── test_pdf_processor.py
│   │   ├── test_chunker.py
│   │   ├── test_embedding_service.py
│   │   ├── test_vector_store.py
│   │   ├── test_rag_orchestrator.py
│   │   └── test_api_endpoints.py
│   └── conftest.py
│
├── docs/
│   ├── REQUIREMENTS.md
│   ├── DESIGN.md
│   └── TASKS.md
│
├── .gitignore
├── README.md
└── .github/
    └── workflows/
        └── ci.yml                  ← Basic lint + test on push
```

---

## 13. State Management Strategy

### Backend State

The backend is designed to be stateless at the HTTP layer. All session state that must persist across requests is stored in one of two places:

1. **ChromaDB (in-memory):** Vector embeddings and chunk metadata. Keyed by session_id via collection naming.
2. **Application-level Python dict:** Document metadata (filename, page_count, chunk_count). Keyed by session_id. This is a simple `dict` stored in `app.state.session_store`.

**Important implication:** Because the backend is deployed to Render's free tier (single instance, restarts on deploy), all session data is lost on restart. This is acceptable and documented behavior for a portfolio application. Users are advised to not rely on long-lived sessions.

### Frontend State

All Streamlit UI state lives in `st.session_state`. The session_id is a UUID4 generated on first page load and stored in session state. It is passed with every API request to the backend.

```python
# state.py — initialization on page load

def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = {}
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "is_querying" not in st.session_state:
        st.session_state.is_querying = False
```

---

## 14. Configuration Management

All configurable values are centralized in `backend/config/settings.py` using `pydantic-settings`.

```python
# config/settings.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Groq
    GROQ_API_KEY: str
    PRIMARY_MODEL: str = "llama-3.3-70b-versatile"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Retrieval
    TOP_K: int = 5
    MAX_HISTORY_TURNS: int = 10
    
    # File upload
    MAX_FILE_SIZE_MB: int = 20
    
    # CORS
    ALLOWED_ORIGINS: str = "https://your-streamlit-app.streamlit.app"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Frontend configuration** (`frontend/.env.example`):
```
BACKEND_URL=https://your-app.onrender.com
```

Loaded in `frontend/api_client.py` via `python-dotenv` or Streamlit's `st.secrets`.

---

## 15. Security Design

### Secret Management

- Groq API key stored only in environment variables
- Never passed to the frontend
- In production, set via Render's "Environment Variables" dashboard (backend) and Streamlit Community Cloud's "Secrets" UI (frontend)
- `.env` files listed in `.gitignore`
- `.env.example` files committed with placeholder values

### CORS Configuration

```python
# main.py

from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

In development: `ALLOWED_ORIGINS=http://localhost:8501`
In production: `ALLOWED_ORIGINS=https://your-app.streamlit.app`

### File Validation

```python
# routers/ingest.py

ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024

async def validate_upload(file: UploadFile):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.")
    return content
```

### No Persistent User Data

Uploaded file bytes are processed in memory and never written to disk in production. ChromaDB uses in-memory mode. No database or file system storage persists beyond the server process lifetime.

---

## 16. Logging Design

### Configuration

```python
# main.py

import logging

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
```

### Logger Usage Pattern

Each module creates its own logger:
```python
logger = logging.getLogger(__name__)
```

### Log Events

| Event | Level | Fields |
|-------|-------|--------|
| Application startup | INFO | model loaded, vector store ready |
| Document upload received | INFO | filename, session_id, file_size |
| Processing complete | INFO | doc_id, page_count, chunk_count, duration_ms |
| Query received | INFO | session_id, query_preview (first 100 chars) |
| Retrieval complete | INFO | session_id, top_k_scores |
| LLM call initiated | INFO | model, message_count |
| LLM streaming complete | INFO | model, token_count_approx |
| LLM rate limit | WARNING | model, retry_count |
| LLM fallback triggered | WARNING | reason, fallback_model |
| Any caught exception | ERROR | exception type, message, stack trace |
| Document deleted | INFO | doc_id, chunks_removed |
| Session cleared | INFO | session_id, docs_removed |

---

## 17. Monitoring Design

### Health Check Implementation

```python
# main.py

@app.get("/health", response_model=HealthResponse)
async def health_check(vector_store: VectorStore = Depends(get_vector_store)):
    vector_store_status = "connected"
    try:
        vector_store.client.heartbeat()
    except Exception:
        vector_store_status = "error"
    
    return HealthResponse(
        status="ok" if vector_store_status == "connected" else "degraded",
        vector_store=vector_store_status,
        timestamp=datetime.utcnow()
    )
```

### Render Health Check Configuration

In the Render dashboard, configure:
- Health check path: `/health`
- Health check interval: 60 seconds

### Usage Metrics Logging

Basic session metrics are emitted as INFO logs at session clear time:
```
INFO | session {id} closed | docs=3 | queries=12 | chunks=512
```

These are visible in Render's log viewer without any additional tooling.

---

## 18. Deployment Architecture

### Infrastructure Overview

```
Developer's Machine
    │
    │ git push origin main
    ▼
GitHub Repository (public)
    │
    ├──────────────────────────────────────────────────┐
    │                                                  │
    ▼                                                  ▼
Render (Backend)                          Streamlit Community Cloud (Frontend)
    │                                                  │
    │ Render watches main branch                       │ Streamlit Cloud watches main branch
    │ Builds from requirements.txt                     │ Builds from requirements.txt
    │ Runs: uvicorn main:app --host 0.0.0.0            │ Runs: streamlit run app.py
    │                                                  │
    ▼                                                  ▼
https://your-backend.onrender.com         https://your-app.streamlit.app
    │                                                  │
    │                                                  │ BACKEND_URL env var
    └──────────────────────────────────────────────────┘
                        (HTTP calls)
```

### Backend Deployment Steps (Render)

1. Create a Render account at render.com
2. Connect GitHub account
3. New Web Service → select repository → select `backend/` as root directory
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Set environment variables in Render dashboard:
   - `GROQ_API_KEY` = [your Groq API key]
   - `ALLOWED_ORIGINS` = [Streamlit Cloud URL, set after frontend deploy]
   - `LOG_LEVEL` = INFO
7. Health check path: `/health`

### Frontend Deployment Steps (Streamlit Community Cloud)

1. Navigate to share.streamlit.io
2. Sign in with GitHub
3. New app → select repository → select `frontend/app.py` as main file
4. Set secrets in Streamlit Cloud UI:
   ```toml
   BACKEND_URL = "https://your-backend.onrender.com"
   ```
5. Deploy

### Procfile (Render alternative)

```
# backend/Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

Note: `--workers 1` is important. Multiple workers would each have their own in-memory ChromaDB instance, causing session inconsistency. A single worker is correct for this architecture.

---

## 19. Design Tradeoffs

| Decision | Tradeoff Accepted | Alternative Rejected | Reason |
|----------|------------------|----------------------|--------|
| ChromaDB in-memory | Data lost on restart | Persistent ChromaDB or external DB | Zero infrastructure cost, sufficient for portfolio use case |
| Single Render worker | No horizontal scaling | Multiple workers | Multiple workers cause session inconsistency with in-memory vector store |
| Session ID in requests (no auth) | No user identity | JWT authentication | Auth adds significant complexity with no benefit for a demo application |
| Sentence Transformers local | Model load time on cold start | OpenAI embeddings API | Free, no API key needed, no rate limits, no external dependency |
| Streamlit for frontend | Limited interactive UI control vs React | React + Vite | Streamlit is a constraint; chosen hosting (Streamlit Community Cloud) is ideal fit |
| RecursiveCharacterTextSplitter | Character-count chunks don't respect semantic boundaries | Semantic chunking | Semantic chunking adds significant complexity and latency; character-count chunks are industry-standard for MVP RAG |
| Conversation history truncation | Oldest context is lost | Summarization of old context | Summarization adds an LLM call per turn; truncation is simpler and sufficient |
| SSE for streaming | Requires SSE parsing in Streamlit client | WebSocket | SSE is simpler, stateless, and sufficient for one-directional streaming |

---

## 20. Future Extension Points

The following extension points are designed into the architecture to enable future enhancements without breaking changes. None of these are implemented in this version.

| Extension | Where | What to Change |
|-----------|-------|----------------|
| Authentication | FastAPI middleware + Streamlit login page | Add JWT middleware; scope session_id to authenticated user |
| Persistent sessions | Replace in-memory stores | Redis for session_store; ChromaDB PersistentClient |
| Semantic chunking | chunker.py | Replace RecursiveCharacterTextSplitter with a semantic splitter |
| Hybrid search | vector_store.py | Add BM25 keyword search; merge with vector scores |
| Multiple embedding models | embedding_service.py | Accept model name as parameter; cache multiple models |
| Reranking | retrieval_service.py | Add cross-encoder reranking step after initial retrieval |
| Multi-user isolation | VectorStore collection naming | Prefix with user_id instead of session_id |
| OpenAI compatibility | llm_client.py | LLMClient interface is model-agnostic; swap Groq for OpenAI SDK |
| Document OCR | pdf_processor.py | Add pytesseract fallback for image-only pages |
| Analytics | New analytics service | Hook into router middleware; emit to a time-series store |

---

*End of DESIGN.md*
