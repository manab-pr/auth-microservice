"""JWT implementation of token generator."""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
from jose import JWTError, jwt
from auth.domain.services import TokenGenerator, TokenData


class JWTTokenGenerator(TokenGenerator):
    """JWT implementation of token generation."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def generate_access_token(
        self, user_id: str, email: str, permissions: List[str] = None
    ) -> str:
        """Generate an access token."""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(
            user_id=user_id,
            email=email,
            permissions=permissions or [],
            expires_delta=expires_delta,
            token_type="access",
        )

    def generate_refresh_token(
        self, user_id: str, email: str, permissions: List[str] = None
    ) -> str:
        """Generate a refresh token."""
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(
            user_id=user_id,
            email=email,
            permissions=permissions or [],
            expires_delta=expires_delta,
            token_type="refresh",
        )

    def decode_token(self, token: str) -> TokenData:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            jti: str = payload.get("jti")
            permissions: List[str] = payload.get("permissions", [])

            if user_id is None or email is None or jti is None:
                raise ValueError("Invalid token payload")

            return TokenData(
                user_id=user_id, email=email, jti=jti, permissions=permissions
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def get_token_expiry_seconds(self, is_refresh: bool = False) -> int:
        """Get the expiry time in seconds for a token."""
        if is_refresh:
            return self.refresh_token_expire_days * 24 * 60 * 60
        return self.access_token_expire_minutes * 60

    def _create_token(
        self,
        user_id: str,
        email: str,
        permissions: List[str],
        expires_delta: timedelta,
        token_type: str,
    ) -> str:
        """Create a JWT token with the given parameters."""
        expire = datetime.utcnow() + expires_delta
        jti = str(uuid.uuid4())  # Unique identifier for the token

        to_encode = {
            "sub": user_id,  # Subject (user ID)
            "email": email,
            "permissions": permissions,  # User permissions
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "jti": jti,  # JWT ID for revocation
            "type": token_type,  # Token type (access or refresh)
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
