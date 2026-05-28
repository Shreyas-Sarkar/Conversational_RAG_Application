from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Request, UploadFile, Query
from fastapi.responses import JSONResponse

try:  # pragma: no cover - import path depends on execution entry point
    from models.metadata import DocumentMetadata
    from models.schemas import ErrorResponse, UploadResponse
except ModuleNotFoundError:  # pragma: no cover
    from backend.models.metadata import DocumentMetadata
    from backend.models.schemas import ErrorResponse, UploadResponse

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
ALLOWED_MIME_TYPES = {"application/pdf"}


@router.post("/upload")
async def upload_document(request: Request, file: UploadFile, session_id: str = Query(...)):
    if file.content_type not in ALLOWED_MIME_TYPES and not file.filename.lower().endswith(".pdf"):
        error = ErrorResponse(
            error="INVALID_FILE_TYPE",
            message="Only PDF files are accepted. Please upload a .pdf file.",
            detail=f"Received MIME type: {file.content_type}",
        )
        return JSONResponse(status_code=400, content=error.model_dump())

    content = await file.read()
    max_bytes = request.app.state.settings.MAX_FILE_SIZE_MB * 1024 * 1024 if hasattr(request.app.state, "settings") else 20 * 1024 * 1024
    if len(content) > max_bytes:
        error = ErrorResponse(
            error="FILE_TOO_LARGE",
            message=f"File exceeds {max_bytes // (1024 * 1024)} MB limit.",
            detail=f"File size: {len(content)} bytes",
        )
        return JSONResponse(status_code=413, content=error.model_dump())

    try:
        pdf_processor = request.app.state.pdf_processor
        chunker = request.app.state.chunker
        embedding_service = request.app.state.embedding_service
        vector_store = request.app.state.vector_store
        storage_service = request.app.state.storage_service

        pages = pdf_processor.extract_text_by_page(content)
        document_id = str(uuid4())
        
        # Upload to Supabase Storage
        public_url = storage_service.upload_document(content, file.filename, document_id)

        chunks = chunker.split_pages_into_chunks(pages, doc_id=document_id, doc_name=file.filename)
        embeddings = embedding_service.generate_embeddings([chunk.text for chunk in chunks])
        uploaded_at = datetime.now(timezone.utc)
        vector_store.upsert_chunks(chunks, embeddings, session_id, uploaded_at=uploaded_at, public_url=public_url)

        session_documents = request.app.state.session_store.setdefault(session_id, {})
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=file.filename,
            page_count=len(pages),
            chunk_count=len(chunks),
            session_id=session_id,
            uploaded_at=uploaded_at,
            public_url=public_url,
        )
        session_documents[document_id] = metadata

        response = UploadResponse(
            document_id=document_id,
            filename=file.filename,
            page_count=len(pages),
            chunk_count=len(chunks),
            status="indexed",
        )
        return JSONResponse(status_code=200, content=response.model_dump())
    except ValueError as exc:
        error = ErrorResponse(error="PROCESSING_ERROR", message=str(exc))
        return JSONResponse(status_code=422, content=error.model_dump())
    except Exception as exc:  # pragma: no cover - defensive boundary
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error during document upload")
        error = ErrorResponse(error="INTERNAL_ERROR", message="An unexpected error occurred during processing.")
        return JSONResponse(status_code=500, content=error.model_dump())
