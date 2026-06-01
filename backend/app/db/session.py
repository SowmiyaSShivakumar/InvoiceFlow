from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class DatabaseSettings:
    database_url: str
    echo: bool = False


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/invoiceflow",
    )


def load_database_settings() -> DatabaseSettings:
    return DatabaseSettings(database_url=get_database_url())

