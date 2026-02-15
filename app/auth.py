"""Compatibility shims for authentication helpers.

This module previously contained its own JWT helpers which conflicted with
the canonical implementations in `app.core.security`. To avoid duplication
and inconsistent behavior, re-export the canonical functions from
`app.core.security` so other modules importing `app.auth` continue to work.
"""

from .core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    oauth2_scheme,
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "get_current_user",
    "oauth2_scheme",
]
