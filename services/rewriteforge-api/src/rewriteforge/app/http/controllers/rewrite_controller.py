from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from rewriteforge.app.http.requests.rewrite_request import RewriteRequest, RewriteResponse
from rewriteforge.app.services.rewrite_service import RewriteService
from rewriteforge.container import Container

router = APIRouter()


@router.post("/v1/rewrite", response_model=RewriteResponse)
@inject
async def rewrite(
    request: RewriteRequest,
    service: RewriteService = Depends(Provide[Container.rewrite_service]),
):
    """Rewrite text in specified style"""
    return await service.rewrite(request.text, request.style)


@router.post("/v1/rewrite/stream")
@inject
async def rewrite_stream(
    request: RewriteRequest,
    service: RewriteService = Depends(Provide[Container.rewrite_service]),
):
    """Rewrite with streaming response (SSE)"""

    async def event_generator():
        async for chunk in service.rewrite_stream(request.text, request.style):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
