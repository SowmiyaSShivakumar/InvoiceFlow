from __future__ import annotations

import time
import unittest

from app.core.security import TokenError, decode_jwt, encode_jwt, hash_password, verify_password


class SecurityTests(unittest.TestCase):
    def test_password_hash_round_trip(self) -> None:
        stored = hash_password("secret-password")
        self.assertTrue(verify_password("secret-password", stored))
        self.assertFalse(verify_password("wrong-password", stored))

    def test_jwt_round_trip(self) -> None:
        token = encode_jwt({"sub": "user-1", "typ": "access", "exp": int(time.time()) + 60}, "top-secret")
        claims = decode_jwt(token, "top-secret")
        self.assertEqual("user-1", claims["sub"])
        self.assertEqual("access", claims["typ"])

    def test_jwt_rejects_wrong_secret(self) -> None:
        token = encode_jwt({"sub": "user-1", "typ": "access", "exp": int(time.time()) + 60}, "top-secret")
        with self.assertRaises(TokenError):
            decode_jwt(token, "different-secret")


if __name__ == "__main__":
    unittest.main()

