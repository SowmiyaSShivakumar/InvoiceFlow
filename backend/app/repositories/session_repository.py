from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.session import AuthSession


class SessionRepository(ABC):
    @abstractmethod
    def create(self, session: AuthSession) -> AuthSession:
        raise NotImplementedError

    @abstractmethod
    def get_by_token_jti(self, token_jti: str) -> AuthSession | None:
        raise NotImplementedError

    @abstractmethod
    def revoke(self, token_jti: str, revoked_at: datetime) -> AuthSession:
        raise NotImplementedError


class InMemorySessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._sessions_by_jti: dict[str, AuthSession] = {}

    def create(self, session: AuthSession) -> AuthSession:
        self._sessions_by_jti[session.token_jti] = session
        return session

    def get_by_token_jti(self, token_jti: str) -> AuthSession | None:
        return self._sessions_by_jti.get(token_jti)

    def revoke(self, token_jti: str, revoked_at: datetime) -> AuthSession:
        session = self._sessions_by_jti.get(token_jti)
        if session is None:
            raise KeyError(f"session not found: {token_jti}")
        revoked_session = AuthSession(
            id=session.id,
            user_id=session.user_id,
            token_jti=session.token_jti,
            expires_at=session.expires_at,
            revoked_at=revoked_at,
            created_at=session.created_at,
        )
        self._sessions_by_jti[token_jti] = revoked_session
        return revoked_session

    def clear(self) -> None:
        self._sessions_by_jti.clear()

