from fastapi import HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit():
    """Get rate limit from settings"""
    if settings.RATE_LIMIT_ENABLED:
        return f"{settings.RATE_LIMIT_PER_MINUTE}/minute"
    return None


def check_rate_limit(request: Request):
    """Check if request is within rate limits"""
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    # Rate limiting is handled by the limiter decorator
    # This function can be used for custom logic if needed
    return True


# Custom rate limit exceeded handler
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "RATE_LIMIT_EXCEEDED",
            "detail": "Too many requests. Please try again later."
        }
    )
