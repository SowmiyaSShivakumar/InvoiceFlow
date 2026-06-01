from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class RegisterRequest:
    email: str
    password: str
    full_name: str | None = None


@dataclass(slots=True)
class LoginRequest:
    email: str
    password: str


@dataclass(slots=True)
class LogoutRequest:
    refresh_token: str


@dataclass(slots=True)
class PublicUser:
    id: str
    email: str
    full_name: str | None
    is_active: bool


@dataclass(slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 0


@dataclass(slots=True)
class AuthResponse:
    user: PublicUser
    tokens: AuthTokens

    def to_dict(self) -> dict[str, object]:
        return {"user": asdict(self.user), "tokens": asdict(self.tokens)}


@dataclass(slots=True)
class MessageResponse:
    detail: str


@dataclass(slots=True)
class MeResponse:
    user: PublicUser

