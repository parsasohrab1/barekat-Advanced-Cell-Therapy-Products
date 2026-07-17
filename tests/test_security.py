"""Tests for security helpers."""

from barekat_cell_therapy.core.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


def test_password_roundtrip():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    token = create_access_token("USR_1", "clinician", "a@b.com")
    payload = verify_access_token(token)
    assert payload["sub"] == "USR_1"
    assert payload["role"] == "clinician"
