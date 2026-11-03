def test_profile_defaults_and_validation(authenticated_client):
    initial = authenticated_client.get("/api/profile")
    assert initial.status_code == 200
    assert initial.json["profile"]["experience_level"] == "beginner"

    invalid = authenticated_client.put("/api/profile", json={
        "experience_level": ["beginner"], "preferred_language": "en",
        "teaching_style": "step-by-step", "learning_goals": "",
    })
    assert invalid.status_code == 400

    valid = authenticated_client.put("/api/profile", json={
        "experience_level": "advanced", "preferred_language": "en",
        "teaching_style": "concise", "learning_goals": "Build reliable APIs",
    })
    assert valid.status_code == 200
    assert valid.json["profile"]["experience_level"] == "advanced"
