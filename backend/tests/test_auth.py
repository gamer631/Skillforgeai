def test_register_and_me(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "display_name": "Test User", "password": "long-password-123"},
    )
    assert response.status_code == 201
    assert response.json["user"]["email"] == "test@example.com"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json["user"]["display_name"] == "Test User"


def test_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "display_name": "Test", "password": "short"},
    )
    assert response.status_code == 400


def test_login_and_logout(client):
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "display_name": "Test", "password": "long-password-123"},
    )
    client.post("/api/auth/logout")
    login = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "long-password-123"}
    )
    assert login.status_code == 200
    assert login.json["user"]["email"] == "test@example.com"
