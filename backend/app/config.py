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
    LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1200"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.4"))
    MAX_USER_MESSAGE_CHARS = int(os.getenv("MAX_USER_MESSAGE_CHARS", "12000"))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    DAILY_CHAT_LIMIT = int(os.getenv("DAILY_CHAT_LIMIT", "30"))

    # PDF processing is bounded; extracted text stays in the database, not public/static storage.
    MAX_PDF_BYTES = int(os.getenv("MAX_PDF_BYTES", str(5 * 1024 * 1024)))
    MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "30"))
    MAX_EXTRACTED_CHARACTERS = int(os.getenv("MAX_EXTRACTED_CHARACTERS", "100000"))
    MAX_PDF_PAGE_CONTENT_BYTES = int(os.getenv("MAX_PDF_PAGE_CONTENT_BYTES", "5000000"))
    MAX_DOCUMENTS_PER_CONVERSATION = int(os.getenv("MAX_DOCUMENTS_PER_CONVERSATION", "5"))

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    WEB_SEARCH_TIMEOUT_SECONDS = int(os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "15"))
    WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SESSION_COOKIE_SECURE = False
    RATELIMIT_ENABLED = False
    LLM_BASE_URL = "http://llm.test/v1"
    LLM_API_KEY = "test-key"
    LLM_MODEL = "test-model"
    TAVILY_API_KEY = ""
    MAX_PDF_BYTES = 5 * 1024 * 1024
    MAX_PDF_PAGES = 3
    MAX_EXTRACTED_CHARACTERS = 10_000
    MAX_PDF_PAGE_CONTENT_BYTES = 100_000
    MAX_DOCUMENTS_PER_CONVERSATION = 3
