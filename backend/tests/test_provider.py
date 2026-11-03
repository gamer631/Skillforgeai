import json

from app.services.llm_provider import OpenAICompatibleProvider


def test_provider_streams_openai_compatible_sse(monkeypatch):
    class FakeResponse:
        ok = True
        text = ""

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def iter_lines(self, decode_unicode=True):
            events = [
                {"choices": [{"delta": {"content": "Hi"}}]},
                {"choices": [{"delta": {"content": " there"}}]},
            ]
            for event in events:
                yield "data: " + json.dumps(event)
            yield "data: [DONE]"

    def fake_post(*_args, **_kwargs):
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_provider.requests.post", fake_post)
    provider = OpenAICompatibleProvider("http://localhost:11434/v1", "", "local-model")
    assert list(provider.stream_chat([{"role": "user", "content": "Hello"}])) == ["Hi", " there"]


def test_provider_requires_model():
    provider = OpenAICompatibleProvider("http://localhost:11434/v1", "", "")
    assert provider.is_configured is False


def test_anthropic_provider_parses_text_delta_events(monkeypatch):
    from app.services.llm_provider import AnthropicMessagesProvider

    class FakeResponse:
        ok = True

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def iter_lines(self, decode_unicode=True):
            yield 'event: content_block_delta'
            yield 'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Claude-style "}}'
            yield 'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"stream"}}'
            yield 'data: {"type":"message_stop"}'

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_provider.requests.post", fake_post)
    provider = AnthropicMessagesProvider(
        "https://api.anthropic.com/v1", "test-key", "test-claude-model", "2026-10-21"
    )
    messages = [
        {"role": "system", "content": "Follow the app rules."},
        {"role": "user", "content": "Hello"},
    ]
    assert list(provider.stream_chat(messages)) == ["Claude-style ", "stream"]
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["json"]["system"] == "Follow the app rules."
    assert captured["json"]["messages"] == [{"role": "user", "content": "Hello"}]
    assert captured["headers"]["anthropic-version"] == "2026-10-21"
