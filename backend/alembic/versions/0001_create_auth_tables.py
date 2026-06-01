"""Create auth tables for InvoiceFlow."""

revision = "0001_create_auth_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade_sql() -> list[str]:
    return [
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL
        );
        """.strip(),
        """
        CREATE TABLE auth_sessions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_jti UUID NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ NULL,
            created_at TIMESTAMPTZ NOT NULL
        );
        """.strip(),
    ]


def downgrade_sql() -> list[str]:
    return [
        "DROP TABLE IF EXISTS auth_sessions;",
        "DROP TABLE IF EXISTS users;",
    ]

