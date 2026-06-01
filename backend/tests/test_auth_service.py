from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.repositories.session_repository import InMemorySessionRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RegisterRequest
from app.services.auth_service import (
    AuthService,
    AuthSettings,
    DuplicateEmailError,
    InvalidCredentialsError,
)


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.users = InMemoryUserRepository()
        self.sessions = InMemorySessionRepository()
        self.service = AuthService(
            self.users,
            self.sessions,
            AuthSettings(secret_key="test-secret", access_token_ttl_seconds=60, refresh_token_ttl_seconds=300),
            now=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    def test_register_creates_user_and_tokens(self) -> None:
        result = self.service.register(RegisterRequest(email="Ayush@example.com", password="Pa55w0rd!", full_name="Ayush"))
        self.assertEqual("ayush@example.com", result.user.email)
        self.assertTrue(result.tokens.access_token)
        self.assertTrue(result.tokens.refresh_token)
        self.assertIsNotNone(self.users.get_by_email("ayush@example.com"))

    def test_register_rejects_duplicate_email(self) -> None:
        self.service.register(RegisterRequest(email="dup@example.com", password="Pa55w0rd!"))
        with self.assertRaises(DuplicateEmailError):
            self.service.register(RegisterRequest(email="dup@example.com", password="AnotherPass!"))

    def test_login_rejects_bad_password(self) -> None:
        self.service.register(RegisterRequest(email="login@example.com", password="Pa55w0rd!"))
        with self.assertRaises(InvalidCredentialsError):
            self.service.login(LoginRequest(email="login@example.com", password="wrong"))

    def test_logout_revokes_session(self) -> None:
        result = self.service.register(RegisterRequest(email="logout@example.com", password="Pa55w0rd!"))
        response = self.service.logout(LogoutRequest(refresh_token=result.tokens.refresh_token))
        self.assertEqual("logged out", response["detail"])
        sessions = list(self.sessions._sessions_by_jti.values())
        self.assertEqual(1, len(sessions))
        self.assertIsNotNone(sessions[0].revoked_at)


if __name__ == "__main__":
    unittest.main()

