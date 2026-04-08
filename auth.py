from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Dict, Optional

from database import User as DbUser, UserRole, get_user_by_username, seed_initial_data, init_db


@dataclass
class AuthUser:
    id: int
    username: str
    name: str
    role: UserRole
    expertise_group: str


# ── In-memory session store ────────────────────────────────────
# Lives as long as the Streamlit server process is running.
# Maps opaque token → AuthUser so page reloads can restore sessions
# without requiring the user to log in again.
_SESSION_STORE: Dict[str, AuthUser] = {}


def create_session(user: AuthUser) -> str:
    """Persist *user* and return a URL-safe token."""
    token = secrets.token_urlsafe(32)
    _SESSION_STORE[token] = user
    return token


def get_session(token: str) -> Optional[AuthUser]:
    """Return the AuthUser for *token*, or None if expired/unknown."""
    return _SESSION_STORE.get(token)


def destroy_session(token: str) -> None:
    """Remove *token* from the store (logout / session invalidation)."""
    _SESSION_STORE.pop(token, None)


# ── DB helpers ────────────────────────────────────────────────

def _ensure_db_seeded() -> None:
    init_db()
    seed_initial_data()


def authenticate(username: str, password: str) -> Optional[AuthUser]:
    """SQLAlchemy üzerinden, schema.ts ile uyumlu Users tablosu bazlı doğrulama."""
    _ensure_db_seeded()
    user: Optional[DbUser] = get_user_by_username(username)
    if not user or user.password != password:
        return None
    return AuthUser(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        expertise_group=user.expertise_group.value,
    )

