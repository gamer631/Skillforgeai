import pytest

from app import create_app
from app.config import TestConfig


class FakeProvider:
    is_configured = True
    model = "fake-model"

    def __init__(self):
        self.last_messages = None

    def stream_chat(self, messages):
        self.last_messages = messages
        yield "I will help you work through this."
        yield " Here is the next step."


@pytest.fixture
def provider():
    return FakeProvider()


@pytest.fixture
def app(provider):
    application = create_app(TestConfig, provider=provider)
    application.config.update(TESTING=True)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "learner@example.com",
            "display_name": "Learner",
            "password": "a-very-secure-password",
        },
    )
    assert response.status_code == 201
    return client
