from typing import Optional

from pydantic import BaseModel, Field


class RewriteRequest(BaseModel):
    """Request validation model"""

    text: str = Field(..., min_length=1, description="Text to rewrite")
    style: Optional[str] = Field(None, description="Target style (pirate, haiku, formal)")


class RewriteResponse(BaseModel):
    """Response model"""

    original: str
    rewritten: str
    style: str
    cached: bool
