from fastapi import Request
from fastapi.responses import JSONResponse

from rewriteforge.app.exceptions import ValidationError


async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc)},
    )
