from fastapi import Request
from fastapi.responses import JSONResponse


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc)},
    )
