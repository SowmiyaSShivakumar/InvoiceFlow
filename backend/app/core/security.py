from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any, Mapping

PASSWORD_HASH_NAME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 310_000
SALT_BYTES = 16
JWT_ALGORITHM = "HS256"


class TokenError(ValueError):
    """Raised when a JWT cannot be verified."""


def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = PASSWORD_ITERATIONS) -> str:
    if not password:
        raise ValueError("password must not be empty")

    salt_bytes = salt or secrets.token_bytes(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return f"{PASSWORD_HASH_NAME}${iterations}${_urlsafe_b64encode(salt_bytes)}${_urlsafe_b64encode(derived_key)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iteration_text, salt_text, hash_text = stored_hash.split("$", 3)
    except ValueError as exc:
        raise ValueError("stored password hash is malformed") from exc

    if algorithm != PASSWORD_HASH_NAME:
        raise ValueError(f"unsupported password hash algorithm: {algorithm}")

    iterations = int(iteration_text)
    salt = _urlsafe_b64decode(salt_text)
    expected_hash = _urlsafe_b64decode(hash_text)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected_hash)


def _json_dumps(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=True).encode("utf-8")


def encode_jwt(payload: Mapping[str, Any], secret: str) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_segment = _urlsafe_b64encode(_json_dumps(header))
    payload_segment = _urlsafe_b64encode(_json_dumps(payload))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_urlsafe_b64encode(signature)}"


def decode_jwt(token: str, secret: str, *, verify_exp: bool = True) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".", 2)
    except ValueError as exc:
        raise TokenError("token is not a valid JWT") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual_signature = _urlsafe_b64decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise TokenError("token signature is invalid")

    header = json.loads(_urlsafe_b64decode(header_segment))
    if header.get("alg") != JWT_ALGORITHM:
        raise TokenError("unsupported JWT algorithm")

    payload = json.loads(_urlsafe_b64decode(payload_segment))
    if verify_exp and "exp" in payload and int(payload["exp"]) < int(time.time()):
        raise TokenError("token has expired")

    return payload


def create_token_payload(*, subject: str, token_type: str, ttl_seconds: int, extra_claims: Mapping[str, Any] | None = None) -> dict[str, Any]:
    issued_at = int(time.time())
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": token_type,
        "iat": issued_at,
        "exp": issued_at + ttl_seconds,
    }
    if extra_claims:
        payload.update(extra_claims)
    return payload


@dataclass(slots=True)
class PasswordSecret:
    value: str

