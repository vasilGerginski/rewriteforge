class RewriteForgeError(Exception):
    """Base exception"""

    pass


class ValidationError(RewriteForgeError):
    """Input validation failed"""

    pass
