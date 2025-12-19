from fastapi import FastAPI

from rewriteforge.app.exceptions import ValidationError
from rewriteforge.app.exceptions.handlers import validation_error_handler
from rewriteforge.container import Container
from rewriteforge.routes.api import api_router


def create_app() -> FastAPI:
    """
    Application factory - Laravel's bootstrap/app.php equivalent.
    """
    # Initialize container
    container = Container()

    # Create FastAPI app
    app = FastAPI(
        title="RewriteForge",
        description="Text rewriting service with pluggable LLM adapters",
        version="1.0.0",
    )

    # Store container reference
    app.container = container

    # Wire container to modules (enables @inject decorator)
    container.wire(
        modules=[
            "rewriteforge.app.http.controllers.rewrite_controller",
        ]
    )

    # Register routes
    app.include_router(api_router)

    # Register exception handlers
    app.add_exception_handler(ValidationError, validation_error_handler)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


# Entry point for uvicorn
app = create_app()
