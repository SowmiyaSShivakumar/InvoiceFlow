from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import uuid4

from app.core.security import (
    TokenError,
    create_token_payload,
    decode_jwt,
    encode_jwt,
    hash_password,
    verify_password,
)
from app.models.session import AuthSession
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    AuthTokens,
    LoginRequest,
    LogoutRequest,
    MeResponse,
    PublicUser,
    RegisterRequest,
)


class AuthError(ValueError):
    pass


class DuplicateEmailError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


@dataclass(slots=True)
class AuthSettings:
    secret_key: str
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        sessions: SessionRepository,
        settings: AuthSettings,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._settings = settings
        self._now = now or (lambda: datetime.now(timezone.utc))

    def register(self, request: RegisterRequest) -> AuthResponse:
        email = self._normalize_email(request.email)
        if self._users.get_by_email(email) is not None:
            raise DuplicateEmailError("email already registered")

        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_password(request.password),
            full_name=self._normalize_full_name(request.full_name),
            is_active=True,
            created_at=self._now(),
            updated_at=self._now(),
        )
        self._users.create(user)
        return self._build_auth_response(user)

    def login(self, request: LoginRequest) -> AuthResponse:
        email = self._normalize_email(request.email)
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("invalid email or password")
        if not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError("invalid email or password")
        return self._build_auth_response(user)

    def logout(self, request: LogoutRequest) -> dict[str, str]:
        claims = self._decode_refresh_token(request.refresh_token)
        token_jti = str(claims["jti"])
        session = self._sessions.get_by_token_jti(token_jti)
        if session is None:
            raise InvalidTokenError("session not found")
        self._sessions.revoke(token_jti, self._now())
        return {"detail": "logged out"}

    def current_user(self, access_token: str) -> MeResponse:
        claims = self._decode_access_token(access_token)
        user = self._users.get_by_id(str(claims["sub"]))
        if user is None or not user.is_active:
            raise InvalidTokenError("user not found")
        return MeResponse(user=self._public_user(user))

    def _build_auth_response(self, user: User) -> AuthResponse:
        access_token = self._issue_access_token(user)
        refresh_token = self._issue_refresh_token(user)
        return AuthResponse(
            user=self._public_user(user),
            tokens=AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self._settings.access_token_ttl_seconds,
            ),
        )

    def _issue_access_token(self, user: User) -> str:
        payload = create_token_payload(
            subject=user.id,
            token_type="access",
            ttl_seconds=self._settings.access_token_ttl_seconds,
            extra_claims={"email": user.email},
        )
        return encode_jwt(payload, self._settings.secret_key)

    def _issue_refresh_token(self, user: User) -> str:
        issued_at = self._now()
        token_jti = str(uuid4())
        expires_at = issued_at + timedelta(seconds=self._settings.refresh_token_ttl_seconds)
        session = AuthSession(
            id=str(uuid4()),
            user_id=user.id,
            token_jti=token_jti,
            expires_at=expires_at,
            revoked_at=None,
            created_at=issued_at,
        )
        self._sessions.create(session)
        payload = create_token_payload(
            subject=user.id,
            token_type="refresh",
            ttl_seconds=self._settings.refresh_token_ttl_seconds,
            extra_claims={"email": user.email, "jti": token_jti},
        )
        return encode_jwt(payload, self._settings.secret_key)

    def _decode_access_token(self, token: str) -> dict[str, object]:
        claims = decode_jwt(token, self._settings.secret_key)
        if claims.get("typ") != "access":
            raise InvalidTokenError("token type must be access")
        return claims

    def _decode_refresh_token(self, token: str) -> dict[str, object]:
        claims = decode_jwt(token, self._settings.secret_key)
        if claims.get("typ") != "refresh":
            raise InvalidTokenError("token type must be refresh")
        return claims

    def _public_user(self, user: User) -> PublicUser:
        return PublicUser(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _normalize_full_name(full_name: str | None) -> str | None:
        if full_name is None:
            return None
        normalized = full_name.strip()
        return normalized or None

