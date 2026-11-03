def _create_project(client, name="SkillForge demo"):
    response = client.post("/api/projects", json={
        "name": name,
        "description": "A Flask API with React frontend for learning.",
        "goals": "Fix authentication and improve the API.",
        "tech_stack": ["Python", "Flask", "React", "MySQL"],
    })
    assert response.status_code == 201
    return response.json["project"]


def test_shared_knowledge_is_seeded_and_listed(authenticated_client):
    response = authenticated_client.get("/api/knowledge")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.json["articles"]}
    assert "python-debugging" in slugs
    assert "machine-learning-workflow" in slugs


def test_project_crud_and_private_file_context(authenticated_client):
    project = _create_project(authenticated_client)
    added = authenticated_client.post(
        f"/api/projects/{project['id']}/files",
        json={
            "path": "backend/auth.py",
            "content": "def require_login(user):\n    if not user:\n        raise PermissionError('authentication required')\n",
        },
    )
    assert added.status_code == 201
    detail = authenticated_client.get(f"/api/projects/{project['id']}")
    assert detail.status_code == 200
    assert detail.json["project"]["files"][0]["path"] == "backend/auth.py"

    updated = authenticated_client.patch(
        f"/api/projects/{project['id']}",
        json={"goals": "Improve login and write regression tests."},
    )
    assert updated.status_code == 200
    assert updated.json["project"]["goals"].startswith("Improve login")

    removed = authenticated_client.delete(
        f"/api/projects/{project['id']}/files/{added.json['file']['id']}"
    )
    assert removed.status_code == 200


def test_project_file_rejects_path_traversal_and_unsupported_files(authenticated_client):
    project = _create_project(authenticated_client)
    traversal = authenticated_client.post(
        f"/api/projects/{project['id']}/files",
        json={"path": "../secrets.env", "content": "SECRET=do-not-store"},
    )
    assert traversal.status_code == 400
    binary = authenticated_client.post(
        f"/api/projects/{project['id']}/files",
        json={"path": "build/app.exe", "content": "not actually a binary"},
    )
    assert binary.status_code == 415


def test_project_isolation_between_users(app, client):
    client.post("/api/auth/register", json={
        "email": "first@example.com", "display_name": "First", "password": "long-password-123",
    })
    project = _create_project(client)
    client.post("/api/auth/logout")
    client.post("/api/auth/register", json={
        "email": "second@example.com", "display_name": "Second", "password": "long-password-123",
    })
    assert client.get(f"/api/projects/{project['id']}").status_code == 404
    assert client.delete(f"/api/projects/{project['id']}").status_code == 404


def test_chat_uses_teaching_mode_shared_knowledge_and_private_project(authenticated_client, provider):
    project = _create_project(authenticated_client)
    file_response = authenticated_client.post(
        f"/api/projects/{project['id']}/files",
        json={
            "path": "backend/auth.py",
            "content": "def authenticate(user):\n    if user is None:\n        raise PermissionError('login required')\n    return user.id\n",
        },
    )
    assert file_response.status_code == 201
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]

    streamed = authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={
            "content": "Explain Python debugging and review this authenticate function.",
            "mode": "teach",
            "project_id": project["id"],
        },
        buffered=True,
    )
    body = streamed.get_data(as_text=True)
    assert streamed.status_code == 200
    assert '"type": "sources"' in body
    system_prompt = provider.last_messages[0]["content"]
    assert "TEACH mode" in system_prompt
    assert "Python debugging" in system_prompt
    assert "backend/auth.py" in system_prompt
    assert "Project name: SkillForge demo" in system_prompt

    detail = authenticated_client.get(f"/api/conversations/{conversation['id']}")
    assistant = detail.json["messages"][-1]
    assert assistant["role"] == "assistant"
    assert any(source["kind"] == "knowledge" for source in assistant["sources"])
    assert any(source["kind"] == "project" for source in assistant["sources"])
    workspace = detail.json["conversation"]["workspace"]
    assert workspace == {"mode": "teach", "project_id": project["id"]}


def test_build_and_review_modes_change_instruction(authenticated_client, provider):
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]
    response = authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Fix the bug", "mode": "build"},
        buffered=True,
    )
    assert response.status_code == 200
    assert "BUILD mode" in provider.last_messages[0]["content"]

    second = authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Review the code", "mode": "review"},
        buffered=True,
    )
    assert second.status_code == 200
    assert "REVIEW mode" in provider.last_messages[0]["content"]


def test_chat_rejects_foreign_project_and_invalid_mode(client):
    client.post("/api/auth/register", json={
        "email": "first@example.com", "display_name": "First", "password": "long-password-123",
    })
    project = _create_project(client)
    client.post("/api/auth/logout")
    client.post("/api/auth/register", json={
        "email": "second@example.com", "display_name": "Second", "password": "long-password-123",
    })
    conversation = client.post("/api/conversations", json={}).json["conversation"]
    foreign = client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Explain this", "mode": "build", "project_id": project["id"]},
    )
    assert foreign.status_code == 404
    invalid = client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Explain this", "mode": "hacker"},
    )
    assert invalid.status_code == 400


def test_learning_profile_personalises_assistant(authenticated_client, provider):
    updated = authenticated_client.put("/api/profile", json={
        "experience_level": "beginner",
        "preferred_language": "ne",
        "learning_goals": "Learn Python and machine learning",
        "teaching_style": "socratic",
    })
    assert updated.status_code == 200
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]
    response = authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Explain variables", "mode": "teach"},
        buffered=True,
    )
    assert response.status_code == 200
    assert "beginner" in provider.last_messages[0]["content"]
    assert "Learn Python and machine learning" in provider.last_messages[0]["content"]
    assert "socratic" in provider.last_messages[0]["content"]


def test_usage_endpoint_reports_estimates(authenticated_client, provider):
    conversation = authenticated_client.post("/api/conversations", json={}).json["conversation"]
    authenticated_client.post(
        f"/api/conversations/{conversation['id']}/messages",
        json={"content": "Explain SQL", "mode": "teach"},
        buffered=True,
    )
    response = authenticated_client.get("/api/usage")
    assert response.status_code == 200
    assert response.json["requests"] == 1
    assert response.json["estimated_input_tokens"] > 0
    assert "estimates" in response.json["note"]
