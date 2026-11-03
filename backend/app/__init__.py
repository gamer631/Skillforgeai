import os

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import csrf, db, limiter
from .services.llm_provider import AnthropicMessagesProvider, OpenAICompatibleProvider


def create_app(config_object=Config, provider=None):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(
        app,
        supports_credentials=True,
        origins=app.config["FRONTEND_ORIGINS"],
        allow_headers=["Content-Type", "X-CSRFToken"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    if provider is not None:
        app.extensions["llm_provider"] = provider
    elif app.config["LLM_PROVIDER"] == "anthropic":
        app.extensions["llm_provider"] = AnthropicMessagesProvider(
            base_url=app.config["LLM_BASE_URL"],
            api_key=app.config["LLM_API_KEY"],
            model=app.config["LLM_MODEL"],
            api_version=app.config["ANTHROPIC_VERSION"],
            timeout=app.config["LLM_TIMEOUT_SECONDS"],
            max_output_tokens=app.config["LLM_MAX_OUTPUT_TOKENS"],
            temperature=app.config["LLM_TEMPERATURE"],
        )
    else:
        app.extensions["llm_provider"] = OpenAICompatibleProvider(
            base_url=app.config["LLM_BASE_URL"],
            api_key=app.config["LLM_API_KEY"],
            model=app.config["LLM_MODEL"],
            timeout=app.config["LLM_TIMEOUT_SECONDS"],
            max_output_tokens=app.config["LLM_MAX_OUTPUT_TOKENS"],
            temperature=app.config["LLM_TEMPERATURE"],
        )

    from .auth.routes import bp as auth_bp
    from .chat.routes import bp as chat_bp
    from .knowledge.routes import bp as knowledge_bp
    from .projects.routes import bp as projects_bp
    from .profile.routes import bp as profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(profile_bp)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "skillforge-ai-api",
            "ai_configured": app.extensions["llm_provider"].is_configured,
            "specialized_modes": ["teach", "build", "review"],
            "project_context_enabled": True,
            "shared_knowledge_enabled": True,
        })

    @app.get("/api/csrf")
    def csrf_token():
        from flask_wtf.csrf import generate_csrf
        return jsonify({"csrf_token": generate_csrf()})

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Invalid request."}), 400

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({"error": "Request exceeds the configured size limit."}), 413

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({"error": "Rate limit reached. Please wait before trying again."}), 429

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
        if app.config["KNOWLEDGE_SEED_ON_STARTUP"]:
            from .knowledge.seed import seed_knowledge_base
            seed_knowledge_base()

    return app
