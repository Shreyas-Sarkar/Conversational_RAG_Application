from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:  # pragma: no cover - import path depends on execution entry point
    from config.settings import get_settings
    from api.routers import documents, ingest, query
    from models.schemas import HealthResponse
    from services.chunker import Chunker
    from services.embedding_service import EmbeddingService
    from services.llm_client import LLMClient
    from services.pdf_processor import PDFProcessor
    from services.rag_orchestrator import RAGOrchestrator
    from services.retrieval_service import RetrievalService
    from services.vector_store import VectorStore
    from services.storage_service import StorageService
except ModuleNotFoundError:  # pragma: no cover
    from backend.config.settings import get_settings
    from backend.api.routers import documents, ingest, query
    from backend.models.schemas import HealthResponse
    from backend.services.chunker import Chunker
    from backend.services.embedding_service import EmbeddingService
    from backend.services.llm_client import LLMClient
    from backend.services.pdf_processor import PDFProcessor
    from backend.services.rag_orchestrator import RAGOrchestrator
    from backend.services.retrieval_service import RetrievalService
    from backend.services.vector_store import VectorStore
    from backend.services.storage_service import StorageService

settings = get_settings()
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    app.state.session_store = {}
    app.state.pdf_processor = PDFProcessor()
    app.state.chunker = Chunker()
    app.state.embedding_service = EmbeddingService()
    app.state.vector_store = VectorStore()
    app.state.storage_service = StorageService()
    app.state.retrieval_service = RetrievalService(app.state.embedding_service, app.state.vector_store)
    app.state.llm_client = LLMClient()
    app.state.rag_orchestrator = RAGOrchestrator()
    yield


app = FastAPI(title="RAG Platform API", version="1.0.0", lifespan=lifespan)
app.state.settings = settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(documents.session_router)
app.include_router(query.router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    vector_store_status = "connected"
    try:
        app.state.vector_store.health_check()
    except Exception:
        vector_store_status = "error"

    return HealthResponse(
        status="ok" if vector_store_status == "connected" else "degraded",
        vector_store=vector_store_status,
        timestamp=datetime.now(timezone.utc),
    )
