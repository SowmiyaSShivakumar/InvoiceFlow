from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Iterable

from app.models.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> User:
        raise NotImplementedError


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}
        self._users_by_email: dict[str, str] = {}

    def get_by_id(self, user_id: str) -> User | None:
        return self._users_by_id.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        user_id = self._users_by_email.get(email.lower())
        if user_id is None:
            return None
        return self._users_by_id.get(user_id)

    def create(self, user: User) -> User:
        normalized_email = user.email.lower()
        if normalized_email in self._users_by_email:
            raise ValueError("email already exists")
        self._users_by_id[user.id] = user
        self._users_by_email[normalized_email] = user.id
        return user

    def update(self, user: User) -> User:
        if user.id not in self._users_by_id:
            raise KeyError(f"user not found: {user.id}")
        self._users_by_id[user.id] = user
        self._users_by_email[user.email.lower()] = user.id
        return user

    def clear(self) -> None:
        self._users_by_id.clear()
        self._users_by_email.clear()

