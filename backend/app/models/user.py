from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class User:
    id: str
    email: str
    password_hash: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def now(cls, **kwargs: object) -> "User":
        now = datetime.now(timezone.utc)
        return cls(created_at=now, updated_at=now, **kwargs)  # type: ignore[arg-type]

