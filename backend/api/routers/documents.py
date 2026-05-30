from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

try:  # pragma: no cover - import path depends on execution entry point
    from models.schemas import ClearSessionResponse, DeleteDocumentResponse, DocumentInfo, DocumentListResponse, ErrorResponse
except ModuleNotFoundError:  # pragma: no cover
    from backend.models.schemas import ClearSessionResponse, DeleteDocumentResponse, DocumentInfo, DocumentListResponse, ErrorResponse

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
session_router = APIRouter(prefix="/api/v1/session", tags=["documents"])


@router.get("")
async def list_documents(request: Request, session_id: str):
    session_documents = request.app.state.session_store.get(session_id, {})
    if not session_documents:
        session_documents = request.app.state.vector_store.get_session_documents(session_id)
        if session_documents:
            request.app.state.session_store[session_id] = session_documents
    documents = [
        DocumentInfo(
            document_id=metadata.document_id if hasattr(metadata, "document_id") else metadata["document_id"],
            filename=metadata.filename if hasattr(metadata, "filename") else metadata["filename"],
            page_count=metadata.page_count if hasattr(metadata, "page_count") else metadata["page_count"],
            chunk_count=metadata.chunk_count if hasattr(metadata, "chunk_count") else metadata["chunk_count"],
            uploaded_at=metadata.uploaded_at if hasattr(metadata, "uploaded_at") else metadata["uploaded_at"],
            public_url=getattr(metadata, "public_url", metadata.get("public_url") if isinstance(metadata, dict) else None),
        )
        for metadata in session_documents.values()
    ]
    response = DocumentListResponse(documents=documents, total_chunks=sum(document.chunk_count for document in documents))
    return JSONResponse(status_code=200, content=response.model_dump(mode="json"))


@router.delete("/{doc_id}")
async def delete_document(request: Request, doc_id: str, session_id: str):
    session_documents = request.app.state.session_store.get(session_id, {})
    if not session_documents:
        session_documents = request.app.state.vector_store.get_session_documents(session_id)
        if session_documents:
            request.app.state.session_store[session_id] = session_documents
    metadata = session_documents.get(doc_id)
    if metadata is None:
        error = ErrorResponse(error="DOCUMENT_NOT_FOUND", message="Document not found in this session.")
        return JSONResponse(status_code=404, content=error.model_dump())

    chunks_removed = request.app.state.vector_store.delete_by_doc_id(doc_id, session_id)
    
    # Delete from Supabase
    filename = getattr(metadata, "filename", metadata.get("filename") if isinstance(metadata, dict) else "unknown.pdf")
    request.app.state.storage_service.delete_document(filename, doc_id)

    del session_documents[doc_id]
    response = DeleteDocumentResponse(deleted=True, document_id=doc_id, chunks_removed=chunks_removed)
    return JSONResponse(status_code=200, content=response.model_dump())


@session_router.delete("/{session_id}")
async def clear_session(request: Request, session_id: str):
    session_documents = request.app.state.session_store.pop(session_id, {})
    if not session_documents:
        session_documents = request.app.state.vector_store.get_session_documents(session_id)
    documents_removed = len(session_documents)
    chunks_removed = 0
    for doc_id, metadata in session_documents.items():
        chunk_count = getattr(metadata, "chunk_count", metadata.get("chunk_count", 0) if isinstance(metadata, dict) else 0)
        chunks_removed += chunk_count
        # Delete from Supabase
        filename = getattr(metadata, "filename", metadata.get("filename") if isinstance(metadata, dict) else "unknown.pdf")
        request.app.state.storage_service.delete_document(filename, doc_id)
    request.app.state.vector_store.delete_collection(session_id)
    response = ClearSessionResponse(
        cleared=True,
        session_id=session_id,
        documents_removed=documents_removed,
        chunks_removed=chunks_removed,
    )
    return JSONResponse(status_code=200, content=response.model_dump())
