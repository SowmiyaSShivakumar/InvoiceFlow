from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class AuthConfig:
    secret_key: str
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30


def load_auth_config() -> AuthConfig:
    return AuthConfig(
        secret_key=os.getenv("AUTH_SECRET_KEY", "change-me-in-production"),
        access_token_ttl_seconds=int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900")),
        refresh_token_ttl_seconds=int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", str(60 * 60 * 24 * 30))),
    )

