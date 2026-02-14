"""
認証API テスト
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """ユーザー登録が成功すること"""
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123", "name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """同じメールアドレスでの登録が失敗すること"""
    payload = {"email": "dup@example.com", "password": "testpass123", "name": "User 1"}
    await client.post("/api/auth/register", json=payload)

    response = await client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "testpass456", "name": "User 2"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """ログインが成功すること"""
    # まず登録
    await client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "testpass123", "name": "Login User"},
    )

    # ログイン
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """パスワード不一致でログインが失敗すること"""
    await client.post(
        "/api/auth/register",
        json={"email": "wrong@example.com", "password": "testpass123", "name": "Wrong User"},
    )

    response = await client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """認証済みユーザー情報取得が成功すること"""
    reg_response = await client.post(
        "/api/auth/register",
        json={"email": "me@example.com", "password": "testpass123", "name": "Me User"},
    )
    token = reg_response.json()["access_token"]

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["name"] == "Me User"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """認証なしでユーザー情報取得が失敗すること"""
    response = await client.get("/api/auth/me")
    assert response.status_code == 403
