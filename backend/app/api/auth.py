from __future__ import annotations

from dataclasses import asdict

from app.schemas.auth import LoginRequest, LogoutRequest, RegisterRequest
from app.services.auth_service import AuthService


class AuthAPI:
    def __init__(self, service: AuthService) -> None:
        self._service = service

    def register(self, payload: RegisterRequest) -> dict[str, object]:
        return self._service.register(payload).to_dict()

    def login(self, payload: LoginRequest) -> dict[str, object]:
        return self._service.login(payload).to_dict()

    def logout(self, payload: LogoutRequest) -> dict[str, object]:
        return self._service.logout(payload)

    def me(self, access_token: str) -> dict[str, object]:
        return {"user": asdict(self._service.current_user(access_token).user)}

