# TASKS.md
# Conversational RAG Platform — Implementation Roadmap

**Version:** 1.0.0
**Status:** Ready for Implementation
**Audience:** Developer executing the build

---

## How to Use This Document

Tasks are ordered sequentially. Each task has a dependency on the tasks before it in the same phase, and each phase depends on the completion of the previous phase unless noted otherwise. Do not skip tasks. Do not reorder phases. Exit criteria must be met before advancing to the next phase.

**Task ID format:** `P{phase}-T{task}`

**Validation notation:**
- ✅ = Automated (run a command to verify)
- 👁 = Manual verification (inspect output or behavior)

---

## Phase 1: Repository Setup

**Goal:** Create a clean, properly structured repository that is ready for code.

**Deliverables:** Public GitHub repository with correct directory structure, gitignore, and README scaffold.

**Dependencies:** GitHub account, Git installed locally.

**Expected Outcome:** A developer can clone the repo and understand the project structure without reading any code.

---

### P1-T1: Create GitHub Repository

**Description:** Create a new public GitHub repository named `rag-platform` (or equivalent).

**Detailed Steps:**
1. Navigate to github.com and sign in
2. Click "New repository"
3. Name: `rag-platform`
4. Visibility: Public (required for Streamlit Community Cloud free tier)
5. Initialize with README: Yes
6. .gitignore template: Python
7. License: MIT
8. Click "Create repository"
9. Clone the repository locally: `git clone https://github.com/your-username/rag-platform.git`
10. Navigate into the repo: `cd rag-platform`

**Completion Criteria:**
- Repository exists at `github.com/your-username/rag-platform`
- Repo is public
- Local clone is ready

**Validation:**
- ✅ `git status` returns `nothing to commit, working tree clean`
- 👁 Repository is visible without login at its GitHub URL

---

### P1-T2: Create Directory Structure

**Description:** Create the complete folder skeleton for the project.

**Detailed Steps:**
1. From the repo root, run:
```bash
mkdir -p backend/api/routers
mkdir -p backend/config
mkdir -p backend/models
mkdir -p backend/services
mkdir -p frontend/components
mkdir -p frontend/styles
mkdir -p frontend/.streamlit
mkdir -p tests/backend
mkdir -p docs
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/api/routers/__init__.py
touch backend/config/__init__.py
touch backend/models/__init__.py
touch backend/services/__init__.py
touch frontend/__init__.py
touch frontend/components/__init__.py
touch tests/__init__.py
touch tests/backend/__init__.py
```

**Completion Criteria:**
- All directories listed in DESIGN.md §12 exist
- All `__init__.py` files are present

**Validation:**
- ✅ `find . -type d | sort` matches the folder structure in DESIGN.md §12
- ✅ `find . -name "__init__.py" | wc -l` returns at least 8

---

### P1-T3: Create .gitignore

**Description:** Extend the default Python .gitignore to exclude environment files, model caches, and deployment artifacts.

**Detailed Steps:**
1. Open `.gitignore` (already created by GitHub)
2. Append the following to the existing Python .gitignore content:
```
# Environment files
.env
.env.local

# Model cache
.cache/
huggingface/
sentence_transformers/

# ChromaDB persistence (if used locally)
chroma_store/

# Streamlit
.streamlit/secrets.toml

# Test artifacts
.pytest_cache/
htmlcov/
.coverage

# macOS
.DS_Store
```
3. Save the file

**Completion Criteria:**
- `.env` would not be tracked by git
- `.streamlit/secrets.toml` would not be tracked

**Validation:**
- ✅ `echo "test" > .env && git status` shows `.env` as untracked (not staged), then `rm .env`
- ✅ `git check-ignore -v .env` returns `.gitignore:.env`

**Common Failure Points:**
- Forgetting to include `.streamlit/secrets.toml` — this causes API key exposure if secrets are ever added and committed

---

### P1-T4: Create README Scaffold

**Description:** Create a README.md with the project description, feature list, architecture overview, setup instructions placeholder, and deployment placeholder.

**Detailed Steps:**
1. Replace the auto-generated `README.md` with:

```markdown
# RAG Platform

A production-style Conversational Retrieval-Augmented Generation (RAG) platform. Upload PDF documents and chat with them using natural language. Built with FastAPI, Streamlit, ChromaDB, Sentence Transformers, and Groq.

## Features

- PDF upload and processing
- Multi-document support
- Semantic retrieval with ChromaDB
- LLM responses grounded in document content
- Source citations with page references
- Conversation history
- Streaming responses
- Neo-Brutalist UI
- Dark/light theme
- Chat export

## Architecture

[See docs/DESIGN.md]

## Local Setup

### Prerequisites
- Python 3.10+
- Groq API key (free at console.groq.com)

### Backend
\`\`\`bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload
\`\`\`

### Frontend
\`\`\`bash
cd frontend
pip install -r requirements.txt
cp .env.example .env
# Set BACKEND_URL=http://localhost:8000 in .env
streamlit run app.py
\`\`\`

## Deployment

[See docs/TASKS.md — Phases 26–27]

## Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/DESIGN.md)
- [Implementation Roadmap](docs/TASKS.md)
```

**Completion Criteria:**
- README is clear, accurate, and includes setup instructions
- All section headers are present

**Validation:**
- 👁 README renders correctly on GitHub

---

### P1-T5: Copy Documentation Files

**Description:** Copy REQUIREMENTS.md, DESIGN.md, and TASKS.md into the `docs/` directory.

**Detailed Steps:**
1. Place this file (TASKS.md) and the other two documents in `docs/`
2. Commit all files created in Phase 1:
```bash
git add .
git commit -m "chore: initialize project structure and documentation"
git push origin main
```

**Completion Criteria:**
- All three documentation files are committed to the `docs/` directory
- README links to all three

**Validation:**
- ✅ `git log --oneline` shows the commit
- 👁 GitHub shows the docs/ directory with all three files

**Phase 1 Exit Criteria:**
- Repository is public on GitHub
- Directory structure matches DESIGN.md §12
- .gitignore is correct
- README is committed
- All documentation is in `docs/`

---

## Phase 2: Project Foundation

**Goal:** Establish Python environments, dependency files, and configuration scaffolds for both backend and frontend.

**Deliverables:** `requirements.txt` files for backend and frontend; `.env.example` files; backend settings module; frontend state module.

**Dependencies:** Phase 1 complete; Python 3.10+ installed.

**Expected Outcome:** Both backend and frontend can be installed locally without errors.

---

### P2-T1: Create Backend requirements.txt

**Description:** Define all backend Python dependencies with minimum version pins.

**Detailed Steps:**
1. Create `backend/requirements.txt`:
```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9
pydantic>=2.7.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.0
httpx>=0.27.0
PyMuPDF>=1.24.0
langchain-text-splitters>=0.2.0
sentence-transformers>=2.7.0
chromadb>=0.5.0
groq>=0.8.0
```

**Completion Criteria:**
- All packages install without conflict

**Validation:**
- ✅ `cd backend && pip install -r requirements.txt` exits with code 0
- ✅ `python -c "import fastapi, uvicorn, fitz, chromadb, groq, sentence_transformers"` imports without error

**Common Failure Points:**
- PyMuPDF requires the package name `PyMuPDF` but imports as `fitz`
- `langchain-text-splitters` is a separate package from `langchain`; do not use `langchain` alone as it pulls in many unneeded dependencies

---

### P2-T2: Create Frontend requirements.txt

**Description:** Define all frontend Python dependencies.

**Detailed Steps:**
1. Create `frontend/requirements.txt`:
```
streamlit>=1.35.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

**Completion Criteria:**
- All packages install without conflict

**Validation:**
- ✅ `cd frontend && pip install -r requirements.txt` exits with code 0
- ✅ `python -c "import streamlit, httpx"` imports without error

---

### P2-T3: Create .env.example Files

**Description:** Create `.env.example` files for both backend and frontend with all required variables documented.

**Detailed Steps:**
1. Create `backend/.env.example`:
```bash
# Required: Your Groq API key (get one free at console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# LLM Models
PRIMARY_MODEL=llama-3.3-70b-versatile
FALLBACK_MODEL=llama-3.1-8b-instant

# Embedding model (downloaded automatically on first run)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chunking parameters
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Retrieval parameters
TOP_K=5
MAX_HISTORY_TURNS=10

# File upload limit in MB
MAX_FILE_SIZE_MB=20

# CORS: comma-separated list of allowed origins
# In development: http://localhost:8501
# In production: your Streamlit Cloud URL
ALLOWED_ORIGINS=http://localhost:8501

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

2. Create `frontend/.env.example`:
```bash
# URL of the deployed FastAPI backend
# In development: http://localhost:8000
# In production: your Render service URL
BACKEND_URL=http://localhost:8000
```

**Completion Criteria:**
- Both files exist and document every configurable variable
- No real secrets are present

**Validation:**
- 👁 Review both files for completeness against DESIGN.md §14
- ✅ `git check-ignore -v backend/.env` confirms .env is ignored; `git check-ignore -v backend/.env.example` confirms .env.example is NOT ignored

---

### P2-T4: Create Backend Settings Module

**Description:** Implement the `pydantic-settings` configuration class.

**Detailed Steps:**
1. Create `backend/config/settings.py` with the full `Settings` class as specified in DESIGN.md §14
2. Implement the `get_settings()` function with `@lru_cache`
3. Test the settings module loads without a `.env` file (only GROQ_API_KEY should cause failure)

**Completion Criteria:**
- `Settings` class loads all variables from environment
- `GROQ_API_KEY` is required (no default); missing it raises a clear `ValidationError`
- All other variables have sensible defaults

**Validation:**
- ✅ `python -c "from config.settings import get_settings; s = get_settings(); print(s.CHUNK_SIZE)"` prints `500` when run with `GROQ_API_KEY=test` set
- ✅ Running without `GROQ_API_KEY` set raises a `ValidationError` with a clear message

**Common Failure Points:**
- Forgetting `class Config: env_file = ".env"` prevents `.env` from being auto-loaded
- Naming the class `Config` (conflicts with the inner `Config` class) — name it `Settings`

---

### P2-T5: Create Frontend State Module

**Description:** Implement the session state initialization function.

**Detailed Steps:**
1. Create `frontend/state.py` with `initialize_session_state()` as specified in DESIGN.md §13
2. Import `uuid` and `streamlit` at the top
3. Implement each key with its correct default type

**Completion Criteria:**
- Function creates all required keys in `st.session_state`
- Calling it twice (idempotent) does not reset existing state

**Validation:**
- 👁 Review code for all required keys from DESIGN.md §13
- ✅ `python -c "from state import initialize_session_state"` imports without error

---

### P2-T6: Create Backend main.py Scaffold

**Description:** Create the FastAPI application entry point with lifespan, CORS, and health check.

**Detailed Steps:**
1. Create `backend/main.py`:
   - Import FastAPI, CORSMiddleware, asynccontextmanager
   - Define the lifespan context manager (empty for now; services added in later phases)
   - Create the FastAPI app with title "RAG Platform API", version "1.0.0"
   - Add CORSMiddleware using settings
   - Add the `/health` route returning `{"status": "ok", "timestamp": datetime.utcnow()}`
   - Configure logging as specified in DESIGN.md §16
2. Start the server: `uvicorn main:app --reload`

**Completion Criteria:**
- Server starts without error
- `/health` returns 200
- `/docs` shows the OpenAPI UI

**Validation:**
- ✅ `curl http://localhost:8000/health` returns `{"status":"ok",...}`
- ✅ `curl http://localhost:8000/docs` returns HTML (200)

**Phase 2 Exit Criteria:**
- `pip install -r requirements.txt` succeeds for both backend and frontend
- Backend server starts and `/health` returns 200
- Settings module loads correctly
- State module imports without error

---

## Phase 3: Backend Setup

**Goal:** Complete the FastAPI application structure with all routers registered and all service stubs in place.

**Deliverables:** All routers registered; all service files created with stub implementations; Pydantic schemas defined.

**Dependencies:** Phase 2 complete.

**Expected Outcome:** The API is navigable via `/docs` and all endpoints return proper 501 or placeholder responses.

---

### P3-T1: Define Pydantic Schemas

**Description:** Implement all request and response schemas from DESIGN.md §7.2 and §7.3.

**Detailed Steps:**
1. Create `backend/models/schemas.py` with:
   - `ConversationMessage`
   - `ChatRequest`
   - `UploadResponse`
   - `DocumentInfo`
   - `DocumentListResponse`
   - `DeleteDocumentResponse`
   - `ClearSessionResponse`
   - `HealthResponse`
   - `ErrorResponse`
2. Create `backend/models/metadata.py` with:
   - `DocumentMetadata` dataclass
   - `Chunk` dataclass
   - `RetrievedChunk` dataclass

**Completion Criteria:**
- All schemas match DESIGN.md §7.2 and §7.3
- All dataclasses have type annotations

**Validation:**
- ✅ `python -c "from models.schemas import ChatRequest, UploadResponse"` imports without error

---

### P3-T2: Create Router Stubs

**Description:** Create all three router files with stub implementations that return 501 Not Implemented.

**Detailed Steps:**
1. Create `backend/api/routers/ingest.py`:
   - Define `router = APIRouter(prefix="/api/v1/documents", tags=["documents"])`
   - Add `POST /upload` stub returning `{"status": "not_implemented"}`
2. Create `backend/api/routers/documents.py`:
   - Define `router = APIRouter(prefix="/api/v1/documents", tags=["documents"])`
   - Add `GET /` stub
   - Add `DELETE /{doc_id}` stub
   - Add `DELETE /session/{session_id}` stub (at `/api/v1/session/{session_id}`)
3. Create `backend/api/routers/query.py`:
   - Define `router = APIRouter(prefix="/api/v1/query", tags=["query"])`
   - Add `POST /chat` stub

**Completion Criteria:**
- All routers import without error
- All routes appear in `/docs`

**Validation:**
- ✅ Visit `http://localhost:8000/docs` and verify all 6 endpoints are listed

---

### P3-T3: Register Routers in main.py

**Description:** Import and register all routers in `main.py`.

**Detailed Steps:**
1. In `backend/main.py`, add:
```python
from api.routers import ingest, query, documents
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(documents.router)
```

**Completion Criteria:**
- All routes appear in `/docs`
- No import errors

**Validation:**
- ✅ `curl http://localhost:8000/docs` shows all endpoints

---

### P3-T4: Create Service Stub Files

**Description:** Create empty stub files for all services so imports work throughout development.

**Detailed Steps:**
1. Create the following files with just a module docstring and an empty class/function stub:
   - `backend/services/pdf_processor.py`
   - `backend/services/chunker.py`
   - `backend/services/embedding_service.py`
   - `backend/services/vector_store.py`
   - `backend/services/retrieval_service.py`
   - `backend/services/llm_client.py`
   - `backend/services/rag_orchestrator.py`
2. Each file should have a `class ServiceName: pass` or equivalent stub

**Validation:**
- ✅ `python -c "from services import pdf_processor, chunker, embedding_service, vector_store, retrieval_service, llm_client, rag_orchestrator"` imports without error

**Phase 3 Exit Criteria:**
- FastAPI server starts without error
- All 6 API endpoints appear in `/docs`
- All service files exist and are importable
- All Pydantic schemas are defined

---

## Phase 4: Frontend Setup

**Goal:** Create a working Streamlit application skeleton that communicates its intent through UI structure.

**Deliverables:** Streamlit app that starts, shows the correct layout structure, and initializes session state.

**Dependencies:** Phase 2 complete.

**Expected Outcome:** Running `streamlit run app.py` shows the application layout with placeholder content.

---

### P4-T1: Create Streamlit Config

**Description:** Configure the base Streamlit theme.

**Detailed Steps:**
1. Create `frontend/.streamlit/config.toml`:
```toml
[theme]
base = "light"
primaryColor = "#FF4B00"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#0A0A0A"
font = "sans serif"

[server]
maxUploadSize = 20
```

**Validation:**
- 👁 Starting the Streamlit app uses these theme colors

---

### P4-T2: Create Component Stub Files

**Description:** Create stub files for all frontend components.

**Detailed Steps:**
1. Create the following with stub functions:
   - `frontend/components/upload.py` → `def render_upload_zone(): st.write("Upload zone placeholder")`
   - `frontend/components/chat.py` → `def render_chat_history(): st.write("Chat placeholder")`
   - `frontend/components/citations.py` → `def render_citations(sources): st.write("Citations placeholder")`
   - `frontend/components/document_panel.py` → `def render_document_panel(): st.write("Document panel placeholder")`
   - `frontend/components/theme_toggle.py` → `def render_theme_toggle(): st.write("Theme toggle")`

**Validation:**
- ✅ All component files import without error

---

### P4-T3: Create API Client Stub

**Description:** Create `frontend/api_client.py` with the full `RAGAPIClient` class structure but stub method bodies.

**Detailed Steps:**
1. Create `frontend/api_client.py` with:
   - `class RAGAPIClient` with `__init__(self, base_url: str)`
   - Method stubs for all operations from DESIGN.md §8 that raise `NotImplementedError`
   - Import `httpx` and `os`
   - Load `BACKEND_URL` from environment

**Validation:**
- ✅ `python -c "from api_client import RAGAPIClient"` imports without error

---

### P4-T4: Create Main app.py

**Description:** Create the Streamlit entry point with the full layout structure.

**Detailed Steps:**
1. Create `frontend/app.py`:
```python
import streamlit as st
from state import initialize_session_state
from components.upload import render_upload_zone
from components.chat import render_chat_history
from components.document_panel import render_document_panel
from components.theme_toggle import render_theme_toggle

st.set_page_config(
    page_title="RAG Platform",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_session_state()

# Sidebar
with st.sidebar:
    render_theme_toggle()
    st.markdown("---")
    render_document_panel()

# Main content
st.title("📄 RAG Platform")
st.caption("Upload PDF documents and chat with them using AI")

if not st.session_state.documents:
    render_upload_zone()
else:
    render_upload_zone()  # always show upload option
    st.markdown("---")
    render_chat_history()
```

**Completion Criteria:**
- `streamlit run app.py` starts without error
- Layout shows sidebar and main content area
- No Python errors in the terminal

**Validation:**
- ✅ `streamlit run app.py` shows the application without error
- 👁 Layout matches the wireframe in DESIGN.md §8

**Phase 4 Exit Criteria:**
- Streamlit app starts without error
- All component stubs are in place
- API client structure is defined
- Session state initializes correctly on load

---

## Phase 5: PDF Processing

**Goal:** Implement PDF text extraction with page-number metadata.

**Deliverables:** Fully implemented `PDFProcessor` service with unit tests.

**Dependencies:** Phase 3 complete.

**Expected Outcome:** A PDF file's text can be extracted into a list of page-content objects with correct page numbers.

---

### P5-T1: Implement PDFProcessor

**Description:** Replace the stub in `pdf_processor.py` with the full implementation.

**Detailed Steps:**
1. Open `backend/services/pdf_processor.py`
2. Implement the class:
```python
import fitz  # PyMuPDF
from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger(__name__)

@dataclass
class PageContent:
    page_number: int  # 1-indexed
    text: str

class PDFProcessor:
    def extract_text_by_page(self, file_bytes: bytes) -> List[PageContent]:
        """
        Extract text from a PDF file given as bytes.
        Returns a list of PageContent objects, one per page with text.
        
        Raises ValueError if:
        - The bytes cannot be parsed as a PDF
        - No text can be extracted from any page
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Could not parse PDF: {str(e)}")
        
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages.append(PageContent(
                    page_number=page_num + 1,  # 1-indexed
                    text=text
                ))
        
        doc.close()
        
        if not pages:
            raise ValueError(
                "No extractable text found in this PDF. "
                "It may be a scanned image-only document."
            )
        
        logger.info(f"Extracted text from {len(pages)} pages")
        return pages
```

**Completion Criteria:**
- Text is extracted correctly from a test PDF
- Page numbers are 1-indexed
- Empty pages are skipped
- ValueError is raised for invalid or image-only PDFs

**Validation:**
- ✅ Unit test: `test_extract_text_by_page_valid_pdf` passes
- ✅ Unit test: `test_extract_text_raises_for_invalid_bytes` passes
- ✅ Unit test: `test_page_numbers_are_one_indexed` passes

---

### P5-T2: Write PDFProcessor Unit Tests

**Description:** Write unit tests for the PDFProcessor service.

**Detailed Steps:**
1. Create `tests/backend/test_pdf_processor.py`
2. Create a fixture that generates a minimal valid PDF in memory using PyMuPDF (to avoid needing a test file)
3. Write tests:
   - `test_extract_text_by_page_valid_pdf`: single-page PDF returns one PageContent
   - `test_multi_page_pdf_returns_correct_count`: 3-page PDF returns 3 PageContent objects
   - `test_page_numbers_are_one_indexed`: first page has page_number=1
   - `test_empty_pages_are_skipped`: a page with no text is not included
   - `test_raises_for_invalid_bytes`: passing `b"not a pdf"` raises ValueError
   - `test_raises_for_image_only_pdf`: (create a PDF with an image and no text layer)

**Validation:**
- ✅ `pytest tests/backend/test_pdf_processor.py -v` all tests pass

**Common Failure Points:**
- PyMuPDF's in-memory PDF creation uses `fitz.open()` with a blank stream; ensure the fixture creates a real PDF structure, not just bytes

**Phase 5 Exit Criteria:**
- PDFProcessor is fully implemented
- All 6 unit tests pass
- Text extraction is validated on at least one real-world PDF manually

---

## Phase 6: Embedding Pipeline

**Goal:** Implement the EmbeddingService that loads the Sentence Transformer model and generates embeddings.

**Deliverables:** Fully implemented `EmbeddingService` with unit tests.

**Dependencies:** Phase 3 complete.

**Expected Outcome:** A list of strings can be converted to 384-dimensional vectors.

---

### P6-T1: Implement EmbeddingService

**Description:** Replace the stub in `embedding_service.py` with the full implementation.

**Detailed Steps:**
1. Implement `EmbeddingService` as specified in DESIGN.md §10:
   - `__init__`: loads `SentenceTransformer(settings.EMBEDDING_MODEL)`, logs model load time
   - `generate_embeddings(texts: List[str]) -> List[List[float]]`: batch encodes, returns as Python lists
   - `generate_embedding(text: str) -> List[float]`: single text, calls generate_embeddings
2. Note: model download (~80 MB) happens on first instantiation; log a message before and after

**Completion Criteria:**
- Model loads successfully
- `generate_embeddings(["hello world"])` returns a list of one 384-element list
- `generate_embedding("hello")` returns a single 384-element list

**Validation:**
- ✅ Unit test: `test_embedding_dimensionality` passes (assert `len(result[0]) == 384`)
- ✅ Unit test: `test_batch_embedding_length` passes
- ✅ Unit test: `test_similar_texts_have_high_cosine_similarity` passes

---

### P6-T2: Write EmbeddingService Unit Tests

**Description:** Write unit tests for the EmbeddingService.

**Detailed Steps:**
1. Create `tests/backend/test_embedding_service.py`
2. Use `@pytest.fixture(scope="module")` to load the model once per test module
3. Write tests:
   - `test_embedding_dimensionality`: single text produces 384-dim vector
   - `test_batch_embedding_length`: N texts produce N embeddings
   - `test_similar_texts_have_high_cosine_similarity`: "dog" and "puppy" have cosine similarity > 0.7
   - `test_dissimilar_texts_have_lower_similarity`: "dog" and "quantum physics" have cosine similarity < 0.5

**Validation:**
- ✅ `pytest tests/backend/test_embedding_service.py -v` all tests pass

**Common Failure Points:**
- Model download may fail in CI environments without internet access; mock the model in CI
- The fixture scope must be `module` not `function` to avoid reloading the model per test

**Phase 6 Exit Criteria:**
- EmbeddingService loads the model and generates correct-dimensional embeddings
- All unit tests pass
- Model download completes and is cached in `.cache/` or the HuggingFace cache dir

---

## Phase 7: Vector Database Integration

**Goal:** Implement the VectorStore service with ChromaDB.

**Deliverables:** Fully implemented `VectorStore` service; ChromaDB integrated in the FastAPI lifespan.

**Dependencies:** Phase 6 complete.

**Expected Outcome:** Chunks can be upserted to and retrieved from ChromaDB.

---

### P7-T1: Implement VectorStore

**Description:** Replace the stub in `vector_store.py` with the full implementation.

**Detailed Steps:**
1. Implement `VectorStore` as specified in DESIGN.md §10:
   - `__init__`: creates `chromadb.Client()` (ephemeral)
   - `get_or_create_collection(session_id: str)`: returns ChromaDB collection named `session_{session_id}`
   - `upsert_chunks(chunks, embeddings, session_id)`: bulk upsert
   - `similarity_search(query_embedding, session_id, top_k, doc_ids_filter=None)`: returns `List[RetrievedChunk]`
   - `delete_by_doc_id(doc_id, session_id)`: deletes by metadata filter
   - `delete_collection(session_id)`: deletes entire collection
   - `health_check()`: calls `self.client.heartbeat()`
2. Update the lifespan in `main.py` to instantiate `VectorStore` and store it in `app.state.vector_store`
3. Update `/health` to call `vector_store.health_check()` and report status

**Completion Criteria:**
- Chunks can be upserted and retrieved in the same session
- Collections are isolated by session_id
- Deleting by doc_id removes only that document's chunks

**Validation:**
- ✅ Unit test: `test_upsert_and_retrieve` passes
- ✅ Unit test: `test_session_isolation` passes (two sessions, search in one returns no results from other)
- ✅ Unit test: `test_delete_by_doc_id` passes
- ✅ `curl http://localhost:8000/health` returns `{"vector_store": "connected"}`

---

### P7-T2: Write VectorStore Unit Tests

**Description:** Write unit tests for the VectorStore service.

**Detailed Steps:**
1. Create `tests/backend/test_vector_store.py`
2. Write tests:
   - `test_upsert_and_retrieve`: insert 10 chunks, query returns up to top_k results
   - `test_session_isolation`: chunks in session A are not retrieved in session B
   - `test_delete_by_doc_id`: deleting doc_id removes its chunks; other docs' chunks remain
   - `test_delete_collection`: after deleting a collection, creating a new one with the same session_id works
   - `test_metadata_preserved_in_results`: retrieved chunks include correct doc_name and page_number

**Validation:**
- ✅ `pytest tests/backend/test_vector_store.py -v` all tests pass

**Phase 7 Exit Criteria:**
- VectorStore is fully implemented
- All unit tests pass
- `/health` reports ChromaDB as connected

---

## Phase 8: Groq Integration

**Goal:** Implement the LLMClient that calls the Groq API with streaming and retry logic.

**Deliverables:** Fully implemented `LLMClient` with streaming, retry, and fallback.

**Dependencies:** Phase 3 complete; Groq API key available.

**Expected Outcome:** A list of messages can be streamed through the Groq API and tokens yielded progressively.

---

### P8-T1: Obtain Groq API Key

**Description:** Register for a Groq account and obtain a free-tier API key.

**Detailed Steps:**
1. Navigate to `console.groq.com`
2. Sign up with GitHub, Google, or email
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key
6. Add to `backend/.env`: `GROQ_API_KEY=your_key_here`

**Validation:**
- 👁 Key is in `.env` and starts with `gsk_`

---

### P8-T2: Implement LLMClient

**Description:** Replace the stub in `llm_client.py` with the full implementation.

**Detailed Steps:**
1. Implement `LLMClient` as specified in DESIGN.md §10:
   - `__init__`: creates `Groq(api_key=settings.GROQ_API_KEY)`
   - `stream_completion(messages, model=None)`: calls Groq with `stream=True`, yields token strings
   - Implements retry on `RateLimitError` with exponential backoff (wait 2s, 4s, 8s)
   - Falls back to `FALLBACK_MODEL` on primary model `RateLimitError` after retry exhaustion, or on 5xx errors
   - Raises final exception if fallback also fails
   - Logs all retry and fallback events at WARNING level

**Completion Criteria:**
- Streaming works: tokens are yielded before the full response is complete
- Fallback is triggered correctly
- Rate limit errors don't crash the application

**Validation:**
- ✅ Manual test: run a simple completion through the client and verify tokens stream
- ✅ Unit test: `test_fallback_triggered_on_rate_limit` passes (mock Groq client)
- 👁 Logs show GROQ API call with model name and token count

---

### P8-T3: Write LLMClient Unit Tests

**Description:** Write unit tests for the LLMClient, mocking the Groq SDK.

**Detailed Steps:**
1. Create `tests/backend/test_llm_client.py`
2. Use `unittest.mock.patch` to mock `groq.Groq`
3. Write tests:
   - `test_stream_yields_tokens`: mock returns 3 chunks; generator yields 3 strings
   - `test_fallback_on_rate_limit`: first call raises RateLimitError; second call (with fallback model) succeeds
   - `test_raises_after_fallback_failure`: both primary and fallback raise; final exception propagates
   - `test_temperature_is_low`: verify `temperature=0.1` is passed (important for RAG grounding)

**Validation:**
- ✅ `pytest tests/backend/test_llm_client.py -v` all tests pass

**Phase 8 Exit Criteria:**
- LLMClient streams tokens from Groq
- Retry and fallback logic is tested
- API key is loaded from environment

---

## Phase 9: Retrieval Pipeline

**Goal:** Implement the full retrieval pipeline: query embedding → vector search → RetrievedChunk list.

**Deliverables:** Fully implemented `RetrievalService`; integration tested with EmbeddingService and VectorStore.

**Dependencies:** Phases 6 and 7 complete.

**Expected Outcome:** A query string produces a ranked list of RetrievedChunk objects with metadata.

---

### P9-T1: Implement Chunker

**Description:** Implement the `Chunker` service before the retrieval service, as it is needed for populating test data.

**Detailed Steps:**
1. Implement `Chunker` in `backend/services/chunker.py` as specified in DESIGN.md §10:
   - `__init__`: creates `RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)`
   - `split_pages_into_chunks(pages, doc_id, doc_name)`: processes each PageContent, assigns metadata, returns `List[Chunk]`
   - Each chunk gets a `uuid4()` chunk_id

**Completion Criteria:**
- A 3-page document is chunked correctly
- Each chunk has correct doc_id, doc_name, page_number, chunk_index
- Chunks from different pages are distinguishable by page_number

**Validation:**
- ✅ Unit test: `test_chunker_preserves_page_numbers` passes

---

### P9-T2: Implement RetrievalService

**Description:** Implement `RetrievalService` that combines EmbeddingService and VectorStore.

**Detailed Steps:**
1. Implement `RetrievalService` in `backend/services/retrieval_service.py`:
```python
class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
    
    def retrieve(
        self, 
        query: str, 
        session_id: str, 
        top_k: int = 5,
        doc_ids_filter: List[str] | None = None
    ) -> List[RetrievedChunk]:
        query_embedding = self.embedding_service.generate_embedding(query)
        return self.vector_store.similarity_search(
            query_embedding, session_id, top_k, doc_ids_filter
        )
```

**Validation:**
- ✅ Integration test: index 5 chunks from a test document, query for one, verify top result is semantically related

**Phase 9 Exit Criteria:**
- Chunker is implemented and tested
- RetrievalService successfully retrieves semantically relevant chunks
- Integration test passes

---

## Phase 10: RAG Orchestration

**Goal:** Implement the RAGOrchestrator that assembles the prompt and ties together retrieval and LLM generation.

**Deliverables:** Fully implemented `RAGOrchestrator` with prompt construction and conversation history handling.

**Dependencies:** Phases 8 and 9 complete.

**Expected Outcome:** A query + context + history produces a correctly formatted message list for the LLM.

---

### P10-T1: Implement RAGOrchestrator

**Description:** Replace the stub in `rag_orchestrator.py` with the full implementation.

**Detailed Steps:**
1. Define the system prompt constant:
```python
RAG_SYSTEM_PROMPT_TEMPLATE = """You are a helpful document assistant. 
Answer questions based ONLY on the context provided below.
If the answer is not present in the context, respond exactly with:
"I cannot find information about this in the uploaded documents."

Do not speculate, invent facts, or use knowledge outside the provided context.
When referencing information, note the document name and page number.

--- DOCUMENT CONTEXT ---
{context_block}
--- END CONTEXT ---"""
```

2. Implement `RAGOrchestrator`:
   - `format_chunks_as_context(chunks: List[RetrievedChunk]) -> str`: formats each chunk with doc_name and page_number header
   - `build_messages(query, retrieved_chunks, conversation_history) -> List[dict]`: assembles the full message list
   - Truncates history to last `MAX_HISTORY_TURNS * 2` messages

**Completion Criteria:**
- Prompt includes context block
- History is truncated correctly
- Message format is OpenAI-compatible (list of `{"role": ..., "content": ...}`)

**Validation:**
- ✅ Unit test: `test_prompt_contains_context` passes
- ✅ Unit test: `test_history_truncation` passes (provide 15 turns, verify only 10 appear)
- ✅ Unit test: `test_no_context_prompt` passes (empty chunks list → empty context block)

---

### P10-T2: Write RAGOrchestrator Unit Tests

**Description:** Write unit tests for prompt construction.

**Detailed Steps:**
1. Create `tests/backend/test_rag_orchestrator.py`
2. Tests:
   - `test_prompt_contains_context`: verify formatted chunks appear in system message
   - `test_history_truncation`: 15 turns → 10 appear in messages
   - `test_context_format_includes_page_numbers`: verify page numbers appear in context block
   - `test_user_message_is_last`: verify the current query is always the last message

**Validation:**
- ✅ `pytest tests/backend/test_rag_orchestrator.py -v` all tests pass

**Phase 10 Exit Criteria:**
- RAGOrchestrator assembles prompts correctly
- History truncation works
- All unit tests pass

---

## Phase 11: API Development

**Goal:** Implement all API endpoints with full business logic, replacing stubs.

**Deliverables:** All 6 endpoints fully functional and tested.

**Dependencies:** Phases 5–10 complete.

**Expected Outcome:** A complete PDF processing and query flow works end-to-end via the API.

---

### P11-T1: Implement Ingest Router

**Description:** Implement `POST /api/v1/documents/upload` in `backend/api/routers/ingest.py`.

**Detailed Steps:**
1. Implement the endpoint:
   - Validate file type and size using `validate_upload()` helper
   - Call `PDFProcessor.extract_text_by_page()`
   - Call `Chunker.split_pages_into_chunks()`
   - Call `EmbeddingService.generate_embeddings()`
   - Call `VectorStore.upsert_chunks()`
   - Store `DocumentMetadata` in `app.state.session_store[session_id][doc_id]`
   - Return `UploadResponse`
2. Wire service dependencies via FastAPI `Depends()` using `request.app.state`
3. Catch all exceptions and return appropriate `ErrorResponse` with correct HTTP codes

**Validation:**
- ✅ `curl -X POST http://localhost:8000/api/v1/documents/upload -F "file=@test.pdf" -F "session_id=test-session"` returns 200 with `UploadResponse`
- ✅ API test: `test_upload_valid_pdf` passes
- ✅ API test: `test_upload_invalid_type_returns_400` passes

---

### P11-T2: Implement Documents Router

**Description:** Implement `GET /api/v1/documents`, `DELETE /api/v1/documents/{doc_id}`, and `DELETE /api/v1/session/{session_id}`.

**Detailed Steps:**
1. `GET /api/v1/documents?session_id={id}`:
   - Read from `app.state.session_store[session_id]`
   - Return `DocumentListResponse`
2. `DELETE /api/v1/documents/{doc_id}?session_id={id}`:
   - Call `VectorStore.delete_by_doc_id()`
   - Remove from `app.state.session_store`
   - Return `DeleteDocumentResponse`
3. `DELETE /api/v1/session/{session_id}`:
   - Call `VectorStore.delete_collection()`
   - Clear session from `app.state.session_store`
   - Return `ClearSessionResponse`

**Validation:**
- ✅ Upload a document, then GET /documents returns it
- ✅ DELETE /documents/{id} removes it; subsequent GET shows it gone
- ✅ DELETE /session clears all documents for the session

---

### P11-T3: Implement Query Router with Streaming

**Description:** Implement `POST /api/v1/query/chat` with SSE streaming.

**Detailed Steps:**
1. Implement the endpoint:
   - Validate session has at least one document
   - Call `RetrievalService.retrieve(query, session_id, top_k)`
   - Call `RAGOrchestrator.build_messages(query, chunks, history)`
   - Return `StreamingResponse` with `media_type="text/event-stream"`
   - The generator yields:
     - `data: {"type":"token","content":"..."}\n\n` for each LLM token
     - `data: {"type":"sources","content":[...]}\n\n` after streaming complete
     - `data: {"type":"done"}\n\n` at end
2. Handle `LLMClient` errors within the generator; yield an error event on failure

**Validation:**
- ✅ `curl -N -X POST http://localhost:8000/api/v1/query/chat -H "Content-Type: application/json" -d '{"session_id":"test","query":"what is this document about?","conversation_history":[]}` streams tokens

---

### P11-T4: Write API Endpoint Tests

**Description:** Write integration tests for all API endpoints.

**Detailed Steps:**
1. Create `tests/backend/test_api_endpoints.py`
2. Use `httpx.AsyncClient` with FastAPI's `TestClient`
3. Tests:
   - `test_health_check`: GET /health returns 200
   - `test_upload_valid_pdf`: POST /upload with valid PDF returns 200 + UploadResponse
   - `test_upload_invalid_type`: POST /upload with .txt file returns 400
   - `test_upload_oversized`: POST /upload with >20 MB returns 413
   - `test_list_documents`: after upload, GET /documents returns the document
   - `test_delete_document`: after upload, DELETE removes it from list
   - `test_chat_no_documents`: POST /chat with no documents returns 404
   - `test_chat_with_document`: full E2E test with mocked Groq (returns one token)

**Validation:**
- ✅ `pytest tests/backend/test_api_endpoints.py -v` all tests pass

**Phase 11 Exit Criteria:**
- All 6 endpoints fully functional
- All API tests pass
- Full end-to-end flow works: upload → query → streaming response

---

## Phase 12: Conversation Memory

**Goal:** Ensure conversation history flows correctly between frontend and backend, and that history is included in prompts.

**Deliverables:** Multi-turn conversation works correctly; history is correctly passed in API calls.

**Dependencies:** Phase 11 complete; Phase 4 complete.

**Expected Outcome:** Asking a follow-up question like "can you elaborate on that?" uses previous context.

---

### P12-T1: Update Session State for Message History

**Description:** Ensure `st.session_state.messages` is correctly appended after each turn.

**Detailed Steps:**
1. In `frontend/components/chat.py`, implement:
   - `render_chat_history()`: renders all messages from `st.session_state.messages`
   - Each user message styled with right-align
   - Each assistant message styled with left-align and a source expander
   - After submission: append user message, call API, stream response, append assistant message with sources

**Validation:**
- 👁 Send 3 messages; all 3 pairs appear in the chat UI in order

---

### P12-T2: Verify History Is Passed in API Calls

**Description:** Ensure the API client sends the correct conversation history to the backend.

**Detailed Steps:**
1. In `frontend/api_client.py`, implement `stream_chat()`:
   - Pass `st.session_state.messages` (excluding `sources` field) as `conversation_history`
   - Strip `sources` field before sending (backend doesn't need it)
2. Verify the backend's `RAGOrchestrator` includes the history in the prompt

**Validation:**
- ✅ Manual test: ask "what is X?", then "tell me more about it" — the assistant's second response should be coherent with the first

---

### P12-T3: Test History Truncation in Production

**Description:** Validate that history truncation doesn't break the conversation flow.

**Detailed Steps:**
1. Set `MAX_HISTORY_TURNS=3` temporarily in settings
2. Send 5 messages
3. Verify the 5th response still works and doesn't include the 1st message in the prompt
4. Restore `MAX_HISTORY_TURNS=10`

**Validation:**
- 👁 No error occurs after truncation; conversation continues normally

**Phase 12 Exit Criteria:**
- Multi-turn conversation works with context
- History is correctly transmitted in API requests
- Truncation does not break conversation flow

---

## Phase 13: Multi-Document Support

**Goal:** Ensure the system correctly handles multiple uploaded documents and retrieves from all of them.

**Deliverables:** Multiple documents can be uploaded and queried simultaneously; citations correctly identify the source document.

**Dependencies:** Phases 11 and 12 complete.

**Expected Outcome:** Uploading two documents and asking a question produces citations from both.

---

### P13-T1: Validate Multi-Document Retrieval

**Description:** Confirm that VectorStore returns results from multiple documents in the same session.

**Detailed Steps:**
1. Upload two different PDFs with distinct content
2. Ask a question that should be answerable from document 1
3. Ask a question that should be answerable from document 2
4. Ask a question that spans both
5. Verify citations include the correct source document in each case

**Validation:**
- 👁 Single-doc question citations only show the relevant document
- 👁 Cross-doc question citations show both documents

---

### P13-T2: Test Document-Level Filtering

**Description:** Verify that filtering by doc_ids works correctly in VectorStore.

**Detailed Steps:**
1. Upload two documents
2. Call `VectorStore.similarity_search()` with `doc_ids_filter=[doc_id_1]`
3. Verify results only contain chunks from document 1
4. Remove the filter and verify results come from both

**Validation:**
- ✅ Unit test: `test_doc_id_filter_restricts_results` passes

**Phase 13 Exit Criteria:**
- Multi-document upload and retrieval works
- Document filtering works correctly
- Citations identify the correct source document

---

## Phase 14: Source Citation System

**Goal:** Implement the full citation extraction, formatting, and display pipeline.

**Deliverables:** Every assistant response includes expandable source citations with document name, page number, and excerpt.

**Dependencies:** Phase 13 complete.

**Expected Outcome:** Each response card shows citation chips that expand to show the source text.

---

### P14-T1: Implement Citation Formatting in RAGOrchestrator

**Description:** Extract citation objects from retrieved chunks after streaming is complete.

**Detailed Steps:**
1. In `rag_orchestrator.py`, add `format_citations(chunks: List[RetrievedChunk]) -> List[dict]`:
   - Deduplicate by (doc_name, page_number) — keep first occurrence
   - Sort by doc_name, then page_number
   - Return: `[{"doc_name": ..., "page": ..., "excerpt": text[:200]}]`

**Validation:**
- ✅ Unit test: `test_format_citations_deduplicates` passes
- ✅ Unit test: `test_format_citations_sorts_by_doc_then_page` passes

---

### P14-T2: Implement Citation Display Component

**Description:** Replace the stub in `frontend/components/citations.py` with the full implementation.

**Detailed Steps:**
1. Implement `render_citations(sources: List[dict])`:
   - For each source, render `st.expander(f"📄 {doc_name} — Page {page}")`
   - Inside the expander, render the excerpt text with `st.caption()`
   - If sources is empty, render nothing

**Validation:**
- 👁 After a query, the citation expander appears below the response
- 👁 Expanding shows the correct page number and excerpt text

---

### P14-T3: Wire Citations Through the Full Stack

**Description:** Ensure citations flow from VectorStore → RAGOrchestrator → API → Streamlit UI.

**Detailed Steps:**
1. Verify the SSE stream emits a `{"type":"sources","content":[...]}` event after the last token
2. Verify the API client in the frontend captures this event
3. Verify the sources are stored in `st.session_state.messages[-1]["sources"]`
4. Verify `render_chat_history()` renders citations for each assistant message

**Validation:**
- 👁 Full flow test: upload PDF, ask question, see streaming response, see citations appear after stream ends

**Phase 14 Exit Criteria:**
- Citations appear for every assistant response
- Citations show correct document name and page number
- Excerpts are visible on expand
- Multi-document sessions show citations from the correct source

---

## Phase 15: Streamlit Chat Experience

**Goal:** Implement the complete, polished chat interface using Streamlit's native chat components.

**Deliverables:** A fully functional chat UI with proper message rendering, input handling, and streaming display.

**Dependencies:** Phase 14 complete.

**Expected Outcome:** The chat experience is smooth, responsive, and visually clear.

---

### P15-T1: Implement Chat History Rendering

**Description:** Replace the stub in `chat.py` with the full chat history renderer.

**Detailed Steps:**
1. Use `st.chat_message("user")` and `st.chat_message("assistant")` for message rendering
2. For user messages: show content and timestamp
3. For assistant messages: show content, timestamp, then render citations below
4. Auto-scroll is handled natively by Streamlit's chat message container

**Validation:**
- 👁 Previous messages are visible when returning to the chat after uploading a new document

---

### P15-T2: Implement Chat Input with Streaming

**Description:** Implement the chat input field and streaming response handler.

**Detailed Steps:**
1. Use `st.chat_input("Ask a question about your documents...")` as the input
2. On submission:
   a. Append user message to session state
   b. Render user message immediately
   c. Show typing indicator (`st.spinner("Thinking...")`)
   d. Call `api_client.stream_chat()` and use `st.write_stream()` to display tokens
   e. After stream ends, capture sources from the last SSE event
   f. Append assistant message (with sources) to session state
   g. Rerender the chat to show citations

**Validation:**
- 👁 Typing a question and pressing Enter shows the response streaming in
- 👁 Citations appear below the response after streaming completes
- 👁 The input field clears after submission

---

### P15-T3: Implement Typing Indicator

**Description:** Show a visual indicator while the backend is processing.

**Detailed Steps:**
1. Set `st.session_state.is_querying = True` before the API call
2. Show `st.spinner()` inside the assistant chat message container while querying
3. Set `st.session_state.is_querying = False` after the stream ends

**Validation:**
- 👁 A spinner appears after submitting a query and before the first token arrives

**Phase 15 Exit Criteria:**
- Chat messages render correctly for both roles
- Responses stream token-by-token
- Citations appear after streaming
- Input field is disabled during streaming

---

## Phase 16: Neo-Brutalist UI

**Goal:** Apply the Neo-Brutalist design language across all interface components.

**Deliverables:** Custom CSS injected via `st.markdown()` that applies the design to all components.

**Dependencies:** Phase 15 complete.

**Expected Outcome:** The application has a distinctive, polished visual identity that matches the Neo-Brutalist specification.

---

### P16-T1: Define the CSS System

**Description:** Create `frontend/styles/neo_brutalist.py` with the complete CSS definition.

**Detailed Steps:**
1. Define the Neo-Brutalist CSS constants:
   - Color palette: `--color-primary: #FF4B00`, `--color-bg: #FFFFFF`, `--color-text: #0A0A0A`, `--color-accent: #FFE600`, `--color-border: #0A0A0A`
   - Border: `2px solid #0A0A0A`
   - Shadow: `4px 4px 0px #0A0A0A`
   - Font: system-ui, bold weight for headings
   - No border-radius on primary elements (or max 2px)
2. Apply styles to:
   - `.stButton > button`: bold border, offset shadow, no radius; hover shifts up-left
   - `.stFileUploader`: dashed border, bold label
   - `.stExpander`: solid border, flat background
   - `.stChatMessage[data-testid="user-message"]`: right-aligned, accent color background
   - `.stChatMessage[data-testid="assistant-message"]`: left-aligned, light gray background
   - Upload zone: large dashed border box
3. Implement `inject_neo_brutalist_css(theme: str)`: calls `st.markdown(css, unsafe_allow_html=True)`

**Validation:**
- 👁 All buttons have visible offset shadows
- 👁 User and assistant messages have distinct background colors
- 👁 No rounded corners on buttons or cards

---

### P16-T2: Apply Theme System

**Description:** Implement dark mode CSS overrides.

**Detailed Steps:**
1. Define dark theme variables: `--color-bg: #0A0A0A`, `--color-text: #FFFFFF`, inverted borders
2. Apply the correct CSS based on `st.session_state.theme`
3. Call `inject_neo_brutalist_css()` at the top of `app.py` before any other render

**Validation:**
- 👁 Toggling theme switches colors for all elements
- 👁 Text is readable in both themes (contrast > 4.5:1)

---

### P16-T3: Style the Upload Zone

**Description:** Apply Neo-Brutalist styling to the upload component.

**Detailed Steps:**
1. In `frontend/components/upload.py`, implement `render_upload_zone()`:
   - Use `st.file_uploader()` for file selection (Streamlit doesn't support native drag-and-drop; the file uploader does support drag-and-drop natively)
   - Wrap in a styled container using `st.markdown()` with a custom CSS class
   - Show upload progress using `st.progress()` while the backend processes

**Validation:**
- 👁 Upload zone has dashed border, upload icon, and label
- 👁 Progress bar appears during processing
- 👁 Success message appears in Neo-Brutalist style

**Phase 16 Exit Criteria:**
- Neo-Brutalist design is applied consistently
- Dark and light themes work
- No soft shadows, gradients, or rounded corners on primary UI elements

---

## Phase 17: Document Management Dashboard

**Goal:** Implement the full document management panel in the sidebar.

**Deliverables:** Sidebar shows document list with metadata and remove controls; session clear button works.

**Dependencies:** Phase 16 complete.

**Expected Outcome:** Users can see their uploaded documents and remove them from the session.

---

### P17-T1: Implement Document Panel Component

**Description:** Replace the stub in `document_panel.py` with the full implementation.

**Detailed Steps:**
1. Implement `render_document_panel()`:
   - If `st.session_state.documents` is empty: show "No documents uploaded yet"
   - For each document: show filename, page count, chunk count, upload timestamp
   - Show a "Remove" button for each document
   - On remove: call `api_client.delete_document(doc_id, session_id)`, remove from `session_state.documents`, rerun
   - Show total chunk count at the bottom
   - Show "Clear Session" button that calls `api_client.clear_session()` and resets all state

**Validation:**
- 👁 Upload a document; it appears in the sidebar with correct metadata
- 👁 Clicking "Remove" removes it from the list
- 👁 "Clear Session" resets the UI to the initial state

---

### P17-T2: Implement Session Status Display

**Description:** Show session stats in the sidebar header.

**Detailed Steps:**
1. Above the document list, show:
   - Number of active documents
   - Total chunks indexed
2. Update dynamically when documents are added or removed

**Validation:**
- 👁 Stats update within 1 second of adding or removing a document

**Phase 17 Exit Criteria:**
- Document panel shows all documents with metadata
- Remove button works and updates the UI
- Clear session resets the full application state

---

## Phase 18: Streaming Responses

**Goal:** Ensure streaming works correctly end-to-end and the frontend displays tokens progressively.

**Deliverables:** Streaming works with correct SSE parsing; no layout jank; citations appear after stream.

**Dependencies:** Phase 15 complete.

**Expected Outcome:** The response appears word-by-word within 5 seconds of submission.

---

### P18-T1: Implement API Client Stream Parser

**Description:** Implement `stream_chat()` in `api_client.py` to correctly parse SSE events.

**Detailed Steps:**
1. Use `httpx.stream()` to open a streaming HTTP connection
2. Parse each `data: {...}` line as JSON
3. Yield token content for `type: "token"` events
4. Capture sources from `type: "sources"` event
5. Stop on `type: "done"` event
6. Make sources accessible after the generator is exhausted (store on the client instance or use a sentinel)

**Implementation approach:**
```python
def stream_chat(self, request: dict) -> Generator:
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", f"{self.base_url}/api/v1/query/chat", json=request) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    if event["type"] == "token":
                        yield event["content"]
                    elif event["type"] == "sources":
                        self._last_sources = event["content"]
                    elif event["type"] == "done":
                        return
```

**Validation:**
- 👁 Response tokens appear progressively in the UI
- ✅ `test_stream_parser_yields_tokens_correctly` passes

---

### P18-T2: Integrate `st.write_stream()` in Chat Component

**Description:** Use Streamlit's native streaming display to show tokens as they arrive.

**Detailed Steps:**
1. In `chat.py`, within the assistant message context:
```python
with st.chat_message("assistant"):
    full_response = st.write_stream(api_client.stream_chat(request))
    sources = api_client._last_sources
    render_citations(sources)
```
2. After `st.write_stream()` completes, append the full response and sources to session state

**Validation:**
- 👁 Tokens stream visually
- 👁 Citations appear after the stream ends without layout shift

**Phase 18 Exit Criteria:**
- Streaming works end-to-end
- Time-to-first-token is under 5 seconds
- Citations appear after streaming completes

---

## Phase 19: Theme System

**Goal:** Implement the dark/light theme toggle with persistent selection within the session.

**Deliverables:** Theme toggle works; all components update on toggle.

**Dependencies:** Phase 16 complete.

**Expected Outcome:** Clicking the theme toggle instantly changes the application's color scheme.

---

### P19-T1: Implement Theme Toggle Component

**Description:** Implement `render_theme_toggle()` in `theme_toggle.py`.

**Detailed Steps:**
1. Implement:
```python
def render_theme_toggle():
    current = st.session_state.theme
    label = "🌙 Dark" if current == "light" else "☀️ Light"
    if st.button(label, key="theme_toggle"):
        st.session_state.theme = "dark" if current == "light" else "light"
        st.rerun()
```
2. Ensure `inject_neo_brutalist_css(st.session_state.theme)` is called in `app.py` before any components render

**Validation:**
- 👁 Toggling changes colors
- 👁 Theme selection persists through chat interactions without resetting

**Phase 19 Exit Criteria:**
- Theme toggle works in both directions
- Theme state persists within the session

---

## Phase 20: Chat Export Features

**Goal:** Implement chat history download functionality.

**Deliverables:** Users can download the conversation as a JSON or text file.

**Dependencies:** Phase 15 complete.

**Expected Outcome:** Clicking "Download Chat" produces a downloadable file with the full conversation.

---

### P20-T1: Implement Chat Export

**Description:** Add a "Download Chat" button that serializes session history to a file.

**Detailed Steps:**
1. In `document_panel.py` (sidebar), below the document list:
```python
if st.session_state.messages:
    export_data = json.dumps(st.session_state.messages, indent=2, default=str)
    st.download_button(
        label="📥 Download Chat",
        data=export_data,
        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
```

**Validation:**
- 👁 Button appears after at least one message
- 👁 Downloaded file contains all messages with timestamps and sources

**Phase 20 Exit Criteria:**
- Download button works
- Exported JSON is valid and contains all messages

---

## Phase 21: Error Handling

**Goal:** Ensure all error states are handled gracefully and communicate clearly to the user.

**Deliverables:** Error handling is implemented at every layer; no stack traces are exposed to the user.

**Dependencies:** Phases 11 and 15 complete.

**Expected Outcome:** Common errors produce friendly messages; the application recovers without reload.

---

### P21-T1: Implement Backend Error Handling

**Description:** Add global exception handlers to FastAPI.

**Detailed Steps:**
1. In `main.py`, add:
```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "PROCESSING_ERROR", "message": str(exc)}
    )

@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please try again."}
    )
```
2. Ensure all service methods raise typed exceptions (ValueError, not generic Exception where possible)

**Validation:**
- ✅ Uploading a non-PDF returns `{"error": "INVALID_FILE_TYPE", ...}` with status 400
- ✅ No stack traces appear in API responses

---

### P21-T2: Implement Frontend Error Handling

**Description:** Add error display for all API call failures.

**Detailed Steps:**
1. Wrap all `api_client` calls in try/except blocks
2. On failure, set `st.session_state.last_error = str(e)` and call `st.rerun()`
3. At the top of `app.py`, check for `st.session_state.last_error` and display it using `st.error()` with a dismiss button
4. Dismiss clears the error from session state

**Validation:**
- 👁 Stop the backend, try to upload a file → "backend unavailable" error appears
- 👁 Error message is in plain English, not a stack trace

---

### P21-T3: Validate All Error Paths

**Description:** Manually test every documented error condition.

**Detailed Steps:**
Test each of the following:
- [ ] Upload non-PDF → 400 error displayed in UI
- [ ] Upload >20 MB file → 413 error displayed in UI
- [ ] Query with no documents → friendly message "Please upload a document first"
- [ ] Groq API key invalid → user sees "unable to generate response" without key exposure
- [ ] Backend offline → user sees "backend unavailable, please try again"

**Validation:**
- 👁 All 5 error conditions produce the correct user-facing message

**Phase 21 Exit Criteria:**
- No error path crashes the application
- All user-facing error messages are in plain English
- No secrets or stack traces are exposed to the user

---

## Phase 22: Logging

**Goal:** Implement comprehensive structured logging across the backend.

**Deliverables:** All significant events are logged with appropriate levels and fields.

**Dependencies:** Phase 21 complete.

**Expected Outcome:** Deployment platform logs are readable and useful for debugging.

---

### P22-T1: Add Logging to All Services

**Description:** Ensure every service logs the events specified in DESIGN.md §16.

**Detailed Steps:**
1. Review each service file against the log events table in DESIGN.md §16
2. Add missing log statements:
   - PDFProcessor: log pages extracted, file size
   - EmbeddingService: log batch size, encoding time
   - VectorStore: log upsert count, search top_k, delete count
   - LLMClient: log model name, retry count, fallback trigger
   - RAGOrchestrator: log prompt length (token estimate), history turn count
3. Add request/response logging middleware:
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration:.1f}ms")
    return response
```

**Validation:**
- 👁 Upload a document; the log shows extraction time, chunk count, embedding time, upsert count
- 👁 Send a query; the log shows retrieval, prompt build, LLM call, stream complete

**Phase 22 Exit Criteria:**
- All services log key events
- Request/response logging is active
- No exception is silently swallowed

---

## Phase 23: Testing

**Goal:** Achieve complete unit and integration test coverage for all backend services and API endpoints.

**Deliverables:** Full test suite passing; test runner configured.

**Dependencies:** All backend phases complete.

**Expected Outcome:** `pytest` runs and all tests pass with no warnings.

---

### P23-T1: Set Up Test Infrastructure

**Description:** Configure pytest and create the conftest with shared fixtures.

**Detailed Steps:**
1. Install test dependencies: `pip install pytest pytest-asyncio httpx`
2. Create `tests/conftest.py`:
   - Fixture: `test_pdf_bytes` — generates a minimal valid PDF in memory using PyMuPDF
   - Fixture: `test_session_id` — returns a fixed UUID string
   - Fixture: `client` — returns a FastAPI TestClient
3. Create `pytest.ini` at repo root:
```ini
[pytest]
testpaths = tests
asyncio_mode = auto
```

**Validation:**
- ✅ `pytest --collect-only` collects all tests without errors

---

### P23-T2: Complete All Remaining Tests

**Description:** Write any remaining unit tests not already created in previous phases.

**Detailed Steps:**
1. Review test coverage for each service:
   - PDFProcessor: complete ✅ (Phase 5)
   - EmbeddingService: complete ✅ (Phase 6)
   - VectorStore: complete ✅ (Phase 7)
   - LLMClient: complete ✅ (Phase 8)
   - Chunker: write `test_chunker.py` with:
     - `test_chunks_have_correct_metadata`
     - `test_chunk_overlap_is_applied`
     - `test_chunk_index_is_sequential`
   - RAGOrchestrator: complete ✅ (Phase 10)
   - API endpoints: complete ✅ (Phase 11)
2. Write any missing tests

**Validation:**
- ✅ `pytest tests/ -v` all tests pass
- ✅ `pytest tests/ --tb=short` shows 0 failures

---

### P23-T3: Run Full Test Suite

**Description:** Run the complete test suite and fix any failures.

**Detailed Steps:**
1. `cd backend && pytest ../tests/ -v`
2. Fix any failing tests
3. Review test output for warnings and address any meaningful warnings

**Validation:**
- ✅ All tests pass with exit code 0
- ✅ No `FAILED` lines in output

**Phase 23 Exit Criteria:**
- All unit and integration tests pass
- `pytest` exits with code 0
- No meaningful warnings

---

## Phase 24: Performance Optimization

**Goal:** Ensure the application meets the performance requirements specified in REQUIREMENTS.md.

**Deliverables:** Performance validation against NFR-01 and NFR-02 targets.

**Dependencies:** Phase 23 complete.

**Expected Outcome:** A 50-page PDF processes in under 60 seconds; first response token arrives in under 5 seconds.

---

### P24-T1: Measure PDF Processing Time

**Description:** Profile document processing and optimize if needed.

**Detailed Steps:**
1. Use a real 50-page PDF
2. Measure: upload time, extraction time, chunking time, embedding time, upsert time
3. If total exceeds 60 seconds, optimize the slowest step:
   - Embedding: ensure batch encoding is used (not per-chunk)
   - Upsert: ensure batch upsert is used (not per-chunk)
4. Log timing results

**Target:** 50-page PDF ≤ 60 seconds total processing

**Validation:**
- 👁 Log output shows timing breakdown within targets

---

### P24-T2: Measure Query Response Latency

**Description:** Profile query end-to-end and verify time-to-first-token.

**Detailed Steps:**
1. With a document indexed, time from query submission to first token received in the UI
2. Break down: embedding time, search time, prompt assembly time, Groq TTFT

**Target:** TTFT ≤ 5 seconds

**Validation:**
- 👁 First token appears in the UI within 5 seconds of pressing Enter

---

### P24-T3: Optimize Embedding Service Initialization

**Description:** Ensure the embedding model loads exactly once and is reused for all requests.

**Detailed Steps:**
1. Verify the `EmbeddingService` is instantiated in the FastAPI lifespan (once at startup)
2. Verify it is injected into routers via `Depends()`, not re-instantiated per request
3. Add a startup log message: "Embedding model loaded in {time}ms"

**Validation:**
- 👁 The model load log message appears once at startup, not on each request

**Phase 24 Exit Criteria:**
- 50-page PDF processes in ≤ 60 seconds
- First response token arrives in ≤ 5 seconds
- Model loads once at startup

---

## Phase 25: Deployment Preparation

**Goal:** Prepare the codebase for production deployment.

**Deliverables:** All deployment configuration files created; environment variables documented; CORS configured for production.

**Dependencies:** Phase 24 complete.

**Expected Outcome:** The application can be deployed to Render and Streamlit Community Cloud without code changes.

---

### P25-T1: Create Backend Procfile

**Description:** Create the Render startup command file.

**Detailed Steps:**
1. Create `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```
2. Note: `--workers 1` is required (see DESIGN.md §18)

**Validation:**
- 👁 File exists with correct content

---

### P25-T2: Verify Production Configuration

**Description:** Ensure all configuration is correct for production.

**Detailed Steps:**
1. Verify `ALLOWED_ORIGINS` in settings supports comma-separated values
2. Verify `LOG_LEVEL=INFO` is the default (not DEBUG)
3. Verify no hardcoded localhost URLs exist in the codebase
4. Run: `grep -r "localhost" backend/` — all occurrences should be in `.env.example` or comments only

**Validation:**
- ✅ `grep -r "localhost" backend/ --include="*.py"` returns 0 results

---

### P25-T3: Final Pre-Deployment Checklist

**Description:** Complete the pre-deployment verification checklist.

**Checklist:**
- [ ] `.env` is in `.gitignore` and not committed
- [ ] `.env.example` is committed and complete
- [ ] `requirements.txt` for backend is correct and installable
- [ ] `requirements.txt` for frontend is correct and installable
- [ ] `Procfile` exists in `backend/`
- [ ] `backend/main.py` starts correctly with `uvicorn`
- [ ] `frontend/app.py` starts correctly with `streamlit run`
- [ ] All tests pass: `pytest tests/ -v`
- [ ] `BACKEND_URL` is loaded from environment in `api_client.py` (not hardcoded)
- [ ] CORS is configured to accept the Streamlit Cloud URL

**Validation:**
- ✅ All checklist items are checked
- ✅ `git status` is clean (all files committed)

---

### P25-T4: Commit All Pre-Deployment Changes

```bash
git add .
git commit -m "feat: complete implementation ready for deployment"
git push origin main
```

**Phase 25 Exit Criteria:**
- All deployment configuration files exist
- Codebase is committed and pushed
- Pre-deployment checklist is complete

---

## Phase 26: Backend Deployment

**Goal:** Deploy the FastAPI backend to Render and verify it is publicly accessible.

**Deliverables:** Live HTTPS backend URL on Render.

**Dependencies:** Phase 25 complete; Render account created.

**Expected Outcome:** `GET https://your-backend.onrender.com/health` returns `{"status":"ok"}`.

---

### P26-T1: Create Render Web Service

**Description:** Configure and deploy the backend on Render.

**Detailed Steps:**
1. Navigate to render.com, sign in, click "New +" → "Web Service"
2. Connect GitHub account and select the `rag-platform` repository
3. Configuration:
   - Name: `rag-platform-backend`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Instance Type: Free
4. Click "Advanced" → add Environment Variables:
   - `GROQ_API_KEY`: your Groq API key
   - `LOG_LEVEL`: INFO
   - `ALLOWED_ORIGINS`: (leave empty for now; update after frontend is deployed)
5. Click "Create Web Service"
6. Wait for the first deploy to complete (5–10 minutes)
7. Note the assigned URL: `https://rag-platform-backend-xxxx.onrender.com`

**Validation:**
- ✅ `curl https://your-backend.onrender.com/health` returns `{"status":"ok",...}`
- ✅ `curl https://your-backend.onrender.com/docs` returns HTML

---

### P26-T2: Configure Health Check on Render

**Description:** Set the health check path in Render's dashboard.

**Detailed Steps:**
1. In the Render service settings, find "Health Check Path"
2. Set to `/health`
3. Save

**Validation:**
- 👁 Render dashboard shows the service as "Live"

---

### P26-T3: Verify Cold-Start Behavior

**Description:** Test the cold-start behavior of the free-tier Render deployment.

**Detailed Steps:**
1. Wait 20+ minutes without activity (Render spins down free tier after ~15 minutes)
2. Send a request to `/health`
3. Measure cold-start time

**Validation:**
- 👁 Service recovers within 60 seconds
- 👁 After recovery, subsequent requests are fast

**Phase 26 Exit Criteria:**
- Backend is publicly accessible at an HTTPS URL
- `/health` returns 200
- Cold-start behavior is documented

---

## Phase 27: Frontend Deployment

**Goal:** Deploy the Streamlit frontend to Streamlit Community Cloud and connect it to the backend.

**Deliverables:** Live HTTPS frontend URL on Streamlit Community Cloud.

**Dependencies:** Phase 26 complete; Streamlit Community Cloud account (free via streamlit.io).

**Expected Outcome:** A public URL shows the full application connected to the live backend.

---

### P27-T1: Deploy to Streamlit Community Cloud

**Description:** Deploy the Streamlit frontend.

**Detailed Steps:**
1. Navigate to share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Repository: `your-username/rag-platform`
5. Branch: `main`
6. Main file path: `frontend/app.py`
7. Click "Advanced settings":
   - Python version: 3.10
   - Secrets:
     ```toml
     BACKEND_URL = "https://your-backend.onrender.com"
     ```
8. Click "Deploy!"
9. Wait for deployment (3–8 minutes)
10. Note the URL: `https://your-app.streamlit.app`

**Validation:**
- 👁 The application loads at the Streamlit Cloud URL
- 👁 Upload a PDF and verify it processes correctly through the live backend

---

### P27-T2: Update Backend CORS Configuration

**Description:** Add the Streamlit Cloud URL to the backend's CORS allowed origins.

**Detailed Steps:**
1. In Render dashboard, update the `ALLOWED_ORIGINS` environment variable:
   - Value: `https://your-app.streamlit.app`
2. Render will redeploy the backend automatically
3. Verify the frontend can now communicate with the backend without CORS errors

**Validation:**
- 👁 Open browser developer tools, upload a file, check Network tab for CORS errors
- ✅ No CORS errors in browser console

---

### P27-T3: Verify Frontend–Backend Connection

**Description:** Complete a full end-to-end test on the live deployment.

**Steps:**
1. Navigate to the Streamlit Cloud URL
2. Upload a PDF
3. Ask a question
4. Verify response streams
5. Verify citations appear
6. Download the chat
7. Toggle the theme
8. Remove the document
9. Verify the document panel updates

**Validation:**
- 👁 All 9 steps complete without error on the live deployment

**Phase 27 Exit Criteria:**
- Frontend is deployed and publicly accessible
- Backend CORS is configured for the frontend URL
- End-to-end functionality verified on live deployment

---

## Phase 28: Production Validation

**Goal:** Systematically validate the deployment against all acceptance criteria from REQUIREMENTS.md §22.

**Deliverables:** All 12 acceptance criteria verified; any issues fixed.

**Dependencies:** Phases 26 and 27 complete.

**Expected Outcome:** The application fully satisfies all requirements for portfolio presentation.

---

### P28-T1: Run Acceptance Criteria Checklist

**Description:** Verify each acceptance criterion from REQUIREMENTS.md §22.

**Checklist:**
- [ ] AC-1: Navigate to public HTTPS URL without login ✅
- [ ] AC-2: Upload PDF, success confirmation within 3 minutes ✅
- [ ] AC-3: Ask question, receive grounded streaming response with citations ✅
- [ ] AC-4: Follow-up questions use conversation context ✅
- [ ] AC-5: Upload multiple documents, receive cross-document citations ✅
- [ ] AC-6: Remove a document from the session ✅
- [ ] AC-7: Download chat history as a file ✅
- [ ] AC-8: Toggle dark/light theme ✅
- [ ] AC-9: Interface usable on 375px mobile viewport ✅
- [ ] AC-10: No paid services required ✅
- [ ] AC-11: README contains sufficient redeployment instructions ✅
- [ ] AC-12: Error states show user-friendly messages without stack traces ✅

**Validation:**
- 👁 All 12 items are checked
- Any failed item must be fixed before marking Phase 28 complete

---

### P28-T2: Mobile Viewport Test

**Description:** Test the application on a 375px viewport.

**Detailed Steps:**
1. Open browser developer tools
2. Set viewport to 375px wide (iPhone SE size)
3. Navigate through: upload, chat, sidebar, theme toggle

**Validation:**
- 👁 No horizontal scrollbar appears
- 👁 Chat input is accessible
- 👁 Upload zone is visible

---

### P28-T3: Error Recovery Test

**Description:** Verify the application recovers from errors without reload.

**Detailed Steps:**
1. Ask a question with no documents uploaded → see friendly error
2. Upload a non-PDF → see correct error message
3. Clear session → UI resets completely
4. Re-upload a document → works normally

**Validation:**
- 👁 All error scenarios produce expected messages and the app continues working

**Phase 28 Exit Criteria:**
- All 12 acceptance criteria verified
- Mobile viewport works
- Error recovery works
- No outstanding bugs

---

## Phase 29: Documentation

**Goal:** Complete all user-facing and developer-facing documentation.

**Deliverables:** Fully completed README with all sections; deployment instructions verified.

**Dependencies:** Phase 28 complete.

**Expected Outcome:** A new developer can clone the repo, set up the project locally, and deploy it by following the README alone.

---

### P29-T1: Complete README

**Description:** Fill in all placeholder sections in the README.

**Detailed Steps:**
1. Add the live demo URL to the top of the README
2. Complete "Local Setup" with exact commands verified to work
3. Complete "Deployment" with step-by-step instructions
4. Add "Architecture" section with a text-based diagram
5. Add "Troubleshooting" section covering common issues:
   - Cold start delay on Render
   - Sentence Transformer model download on first run
   - CORS errors after frontend deployment
   - Image-only PDF rejection

**Validation:**
- 👁 Follow the README on a fresh machine (or fresh virtual environment) and verify it works end-to-end

---

### P29-T2: Add Code Docstrings

**Description:** Ensure all public functions and classes have docstrings.

**Detailed Steps:**
1. Scan all files in `backend/services/` and `backend/api/routers/`
2. Add docstrings to any function or class missing one
3. Docstring format: one-line summary, optional Args/Returns/Raises sections

**Validation:**
- ✅ `python -m pydoc backend/services/pdf_processor.py` shows documentation

**Phase 29 Exit Criteria:**
- README is complete and verified
- All public functions have docstrings
- Troubleshooting section covers the 4 most common issues

---

## Phase 30: Portfolio Readiness

**Goal:** Ensure the project is ready to be presented as a portfolio piece.

**Deliverables:** Project metadata, screenshots, architecture diagram, and GitHub presentation are complete.

**Dependencies:** Phase 29 complete.

**Expected Outcome:** A recruiter or interviewer can evaluate the project from GitHub without running it locally.

---

### P30-T1: Add Screenshots to README

**Description:** Capture and add screenshots of the application to the README.

**Detailed Steps:**
1. Capture screenshots of:
   - Initial state (upload zone)
   - After uploading a document (document panel visible)
   - Chat conversation with citations visible
   - Dark theme view
   - Mobile viewport view
2. Save to `docs/screenshots/`
3. Add to README using relative paths

**Validation:**
- 👁 Screenshots display correctly on GitHub's README renderer

---

### P30-T2: Add Architecture Diagram to README

**Description:** Add a simplified architecture diagram to the README.

**Detailed Steps:**
1. Use the text-based diagram from DESIGN.md §5.1 (simplified)
2. Alternatively, generate a simple diagram using Mermaid (GitHub renders Mermaid natively):
```markdown
\`\`\`mermaid
graph LR
    User -->|upload/chat| Frontend[Streamlit\nFrontend]
    Frontend -->|REST/SSE| Backend[FastAPI\nBackend]
    Backend -->|query| ChromaDB[(ChromaDB\nVector Store)]
    Backend -->|generate| Groq[Groq API\nLLaMA 3.3 70B]
    Backend -->|embed| ST[Sentence\nTransformers]
\`\`\`
```

**Validation:**
- 👁 Diagram renders correctly on GitHub

---

### P30-T3: GitHub Repository Presentation

**Description:** Ensure the GitHub repository is ready for portfolio presentation.

**Detailed Steps:**
1. Add repository description: "Production-style Conversational RAG platform. Upload PDFs, chat with them using AI. Built with FastAPI, Streamlit, ChromaDB, and Groq."
2. Add repository topics: `rag`, `llm`, `fastapi`, `streamlit`, `chromadb`, `groq`, `nlp`, `python`, `ai`, `portfolio`
3. Add the live demo URL to the repository "Website" field
4. Ensure the repository is public
5. Pin the repository to your GitHub profile

**Validation:**
- 👁 Repository page shows description, topics, and live URL
- 👁 Repository appears in profile's pinned repositories

---

### P30-T4: Final Review

**Description:** Conduct a final review of the complete project.

**Checklist:**
- [ ] Live application is accessible at the public URL
- [ ] All features from REQUIREMENTS.md §3 are implemented and working
- [ ] All acceptance criteria from REQUIREMENTS.md §22 are met
- [ ] README is complete with screenshots and architecture diagram
- [ ] No TODO comments remain in the codebase
- [ ] No hardcoded secrets in any committed file
- [ ] All tests pass
- [ ] CORS is configured correctly
- [ ] Error handling is complete
- [ ] Logging is complete
- [ ] Documentation files are in `docs/`

**Validation:**
- 👁 All checklist items checked
- 👁 Perform a final demonstration of the full feature set on the live URL

---

**🎉 Public production deployment completed.**

The Conversational RAG Platform is complete. The system is:
- Publicly accessible at a zero-cost HTTPS URL
- Fully implemented per the requirements in REQUIREMENTS.md
- Architecturally sound per the design in DESIGN.md
- Documented for re-deployment by any developer

---

## Common Failure Points Reference

| Phase | Failure | Diagnosis | Fix |
|-------|---------|-----------|-----|
| P5 | Text extraction returns empty | PDF is image-only | Implement image-only check; reject with clear error |
| P6 | Model download fails | No internet in environment | Use `HF_HOME` env var to point to cached model |
| P7 | ChromaDB collection collision | Same session_id reused | Always use UUID4 for session_id; check initialization |
| P8 | Groq rate limit during demo | Too many rapid queries | Demo with slower pacing; implement retry |
| P11 | CORS error in browser | `ALLOWED_ORIGINS` not set | Update Render env var after frontend deploys |
| P15 | Streamlit reruns on every widget interaction | Default Streamlit behavior | Use `st.session_state` to preserve state |
| P18 | SSE stream not parsed correctly | Missing `data: ` prefix | Strip `data: ` before JSON parsing |
| P26 | Render deploy fails | Missing `Procfile` or `requirements.txt` | Verify root directory is `backend` in Render settings |
| P27 | Streamlit Cloud can't find main file | Wrong path set | Main file path must be `frontend/app.py` |
| P27 | Backend unreachable from Streamlit | `BACKEND_URL` not set in Secrets | Add to Streamlit Cloud secrets, not `.env` |

---

*End of TASKS.md*
