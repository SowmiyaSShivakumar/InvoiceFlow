from __future__ import annotations

from app.core.config import load_auth_config
from app.api.auth import AuthAPI
from app.repositories.session_repository import InMemorySessionRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RegisterRequest
from app.services.auth_service import AuthService, AuthSettings, DuplicateEmailError, InvalidCredentialsError, InvalidTokenError

try:
    from fastapi import FastAPI, HTTPException, Header
except ImportError:  # pragma: no cover - optional runtime dependency
    FastAPI = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]


def build_auth_api() -> AuthAPI:
    users = InMemoryUserRepository()
    sessions = InMemorySessionRepository()
    auth_config = load_auth_config()
    settings = AuthSettings(
        secret_key=auth_config.secret_key,
        access_token_ttl_seconds=auth_config.access_token_ttl_seconds,
        refresh_token_ttl_seconds=auth_config.refresh_token_ttl_seconds,
    )
    return AuthAPI(AuthService(users, sessions, settings))


def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("fastapi is not installed")

    app = FastAPI(title="InvoiceFlow API")
    auth_api = build_auth_api()

    @app.post("/auth/register")
    def register(payload: RegisterRequest) -> dict[str, object]:
        try:
            return auth_api.register(payload)
        except DuplicateEmailError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/auth/login")
    def login(payload: LoginRequest) -> dict[str, object]:
        try:
            return auth_api.login(payload)
        except InvalidCredentialsError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @app.post("/auth/logout")
    def logout(payload: LogoutRequest) -> dict[str, object]:
        try:
            return auth_api.logout(payload)
        except InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @app.get("/auth/me")
    def me(authorization: str | None = Header(default=None)) -> dict[str, object]:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        token = authorization.removeprefix("Bearer ").strip()
        try:
            return auth_api.me(token)
        except InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    return app


app = create_app() if FastAPI is not None else None
