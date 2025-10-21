"""Rate limiting middleware."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter instance
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Rate limit handler
rate_limit_handler = _rate_limit_exceeded_handler
