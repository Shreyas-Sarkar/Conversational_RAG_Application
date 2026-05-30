import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

try:  # pragma: no cover - import path depends on execution entry point
    from models.schemas import ChatRequest, ErrorResponse
except ModuleNotFoundError:  # pragma: no cover
    from backend.models.schemas import ChatRequest, ErrorResponse

router = APIRouter(prefix="/api/v1/query", tags=["query"])


@router.post("/chat")
async def chat(request: Request, body: ChatRequest):
    session_documents = request.app.state.session_store.get(body.session_id, {})
    if not session_documents:
        session_documents = request.app.state.vector_store.get_session_documents(body.session_id)
        if session_documents:
            request.app.state.session_store[body.session_id] = session_documents
    if not session_documents:
        error = ErrorResponse(error="NO_DOCUMENTS", message="Please upload a document first.")
        return JSONResponse(status_code=404, content=error.model_dump())

    async def event_stream():
        try:
            retrieval_service = request.app.state.retrieval_service
            rag_orchestrator = request.app.state.rag_orchestrator
            llm_client = request.app.state.llm_client

            retrieved_chunks = retrieval_service.retrieve(
                query=body.query,
                session_id=body.session_id,
                top_k=body.top_k,
            )
            history = [message.model_dump() for message in body.conversation_history]
            messages = rag_orchestrator.build_messages(body.query, retrieved_chunks, history)

            for token in llm_client.stream_completion(messages):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            sources = rag_orchestrator.format_citations(retrieved_chunks)
            yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as exc:  # pragma: no cover - defensive boundary
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Unexpected error during streaming chat")
            error = ErrorResponse(error="QUERY_FAILED", message="Unable to generate response.")
            yield f"data: {json.dumps({'type': 'error', 'content': error.model_dump()})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
