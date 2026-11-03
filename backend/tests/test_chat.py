def test_conversation_requires_authentication(client):
    response = client.get("/api/conversations")
    assert response.status_code == 401


def test_create_and_stream_message(authenticated_client, provider):
    created = authenticated_client.post("/api/conversations", json={})
    assert created.status_code == 201
    conversation_id = created.json["conversation"]["id"]

    response = authenticated_client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"content": "Explain Python variables in simple terms."},
        buffered=True,
    )
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '"content": "Hello "' in body
    assert '"type": "done"' in body
    assert provider.last_messages[-1]["content"] == "Explain Python variables in simple terms."

    history = authenticated_client.get(f"/api/conversations/{conversation_id}")
    assert history.status_code == 200
    assert [item["role"] for item in history.json["messages"]] == ["user", "assistant"]
    assert history.json["messages"][1]["content"] == "Hello from SkillForge AI."


def test_user_cannot_access_another_users_conversation(app, client):
    client.post(
        "/api/auth/register",
        json={"email": "first@example.com", "display_name": "First", "password": "long-password-123"},
    )
    conversation = client.post("/api/conversations", json={}).json["conversation"]
    client.post("/api/auth/logout")
    client.post(
        "/api/auth/register",
        json={"email": "second@example.com", "display_name": "Second", "password": "long-password-123"},
    )
    response = client.get(f"/api/conversations/{conversation['id']}")
    assert response.status_code == 404


def test_rejects_empty_message(authenticated_client):
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]
    response = authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages", json={"content": "   "}
    )
    assert response.status_code == 400


def test_delete_conversation(authenticated_client):
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]
    response = authenticated_client.delete(f"/api/conversations/{conversation['id']}")
    assert response.status_code == 200
    assert authenticated_client.get(f"/api/conversations/{conversation['id']}").status_code == 404
