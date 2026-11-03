import os
from datetime import timedelta


def _as_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-development-only-change-before-deploy")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///skillforge_ai.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _as_bool("SESSION_COOKIE_SECURE", False)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    WTF_CSRF_TIME_LIMIT = 60 * 60 * 8
    FRONTEND_ORIGINS = [
        value.strip()
        for value in os.getenv(
            "FRONTEND_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if value.strip()
    ]
    RATELIMIT_DEFAULT = "300 per hour"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai-compatible").strip().lower()
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    ANTHROPIC_VERSION = os.getenv("ANTHROPIC_VERSION", "2026-10-21")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "")
    LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
    LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1600"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.35"))
    MAX_USER_MESSAGE_CHARS = int(os.getenv("MAX_USER_MESSAGE_CHARS", "12000"))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    DAILY_CHAT_LIMIT = int(os.getenv("DAILY_CHAT_LIMIT", "30"))

    MAX_PROJECTS_PER_USER = int(os.getenv("MAX_PROJECTS_PER_USER", "10"))
    MAX_PROJECT_FILES = int(os.getenv("MAX_PROJECT_FILES", "30"))
    MAX_PROJECT_FILE_CHARS = int(os.getenv("MAX_PROJECT_FILE_CHARS", "40000"))
    MAX_PROJECT_TOTAL_CHARS = int(os.getenv("MAX_PROJECT_TOTAL_CHARS", "250000"))
    MAX_RETRIEVAL_CHUNKS = int(os.getenv("MAX_RETRIEVAL_CHUNKS", "6"))
    MAX_RETRIEVAL_CONTEXT_CHARS = int(os.getenv("MAX_RETRIEVAL_CONTEXT_CHARS", "10000"))
    KNOWLEDGE_SEED_ON_STARTUP = _as_bool("KNOWLEDGE_SEED_ON_STARTUP", True)


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SESSION_COOKIE_SECURE = False
    RATELIMIT_ENABLED = False
    LLM_BASE_URL = "http://llm.test/v1"
    LLM_API_KEY = "test-key"
    LLM_MODEL = "test-model"
    MAX_PROJECTS_PER_USER = 3
    MAX_PROJECT_FILES = 3
    MAX_PROJECT_FILE_CHARS = 5000
    MAX_PROJECT_TOTAL_CHARS = 10000
    KNOWLEDGE_SEED_ON_STARTUP = True
