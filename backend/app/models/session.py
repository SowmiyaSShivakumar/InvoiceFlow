from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AuthSession:
    id: str
    user_id: str
    token_jti: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime

    def is_active(self, now: datetime) -> bool:
        return self.revoked_at is None and self.expires_at > now

