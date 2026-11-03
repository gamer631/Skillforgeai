import hashlib
import posixpath
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func

from ..auth.routes import current_user
from ..extensions import db, limiter
from ..models import Project, ProjectFile

bp = Blueprint("projects", __name__, url_prefix="/api/projects")

ALLOWED_EXTENSIONS = {
    ".py": "python", ".pyi": "python", ".js": "javascript", ".jsx": "jsx",
    ".ts": "typescript", ".tsx": "tsx", ".html": "html", ".css": "css",
    ".scss": "scss", ".json": "json", ".md": "markdown", ".txt": "text",
    ".sql": "sql", ".yml": "yaml", ".yaml": "yaml", ".toml": "toml",
    ".sh": "shell", ".bash": "shell", ".env.example": "text",
    ".java": "java", ".go": "go", ".rs": "rust", ".php": "php",
    ".rb": "ruby", ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
    ".cs": "csharp", ".kt": "kotlin", ".swift": "swift", ".dart": "dart",
    ".vue": "vue", ".svelte": "svelte", ".xml": "xml", ".graphql": "graphql",
    ".prisma": "prisma", ".ini": "ini", ".cfg": "ini",
}


def owned_project(project_id: int, user_id: int):
    return Project.query.filter_by(id=project_id, user_id=user_id).first()


def _normalise_path(value: str):
    path = str(value or "").replace("\\", "/").strip()
    if not path or len(path) > 240 or path.startswith("/") or "\x00" in path:
        return None
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts) or ":" in parts[0]:
        return None
    normal = posixpath.normpath(path)
    if normal.startswith("../") or normal == "..":
        return None
    return normal


@bp.get("")
def list_projects():
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    projects = Project.query.filter_by(user_id=user.id).order_by(Project.updated_at.desc()).all()
    return jsonify({"projects": [item.to_dict() for item in projects]})


@bp.post("")
@limiter.limit("10 per hour")
def create_project():
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    if Project.query.filter_by(user_id=user.id).count() >= current_app.config["MAX_PROJECTS_PER_USER"]:
        return jsonify({"error": "Project limit reached for this beta account."}), 429
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    goals = str(data.get("goals", "")).strip()
    stack = data.get("tech_stack", [])
    if not name or len(name) > 120:
        return jsonify({"error": "Project name is required and must be under 120 characters."}), 400
    if len(description) > 3000 or len(goals) > 2000:
        return jsonify({"error": "Project description or goals are too long."}), 400
    if not isinstance(stack, list) or len(stack) > 20 or any(not isinstance(x, str) for x in stack):
        return jsonify({"error": "tech_stack must be a list of up to 20 strings."}), 400
    project = Project(
        user_id=user.id, name=name, description=description, goals=goals,
        tech_stack=", ".join(part.strip()[:40] for part in stack if part.strip()),
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"project": project.to_dict(include_files=True)}), 201


@bp.get("/<int:project_id>")
def get_project(project_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    project = owned_project(project_id, user.id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    return jsonify({"project": project.to_dict(include_files=True)})


@bp.patch("/<int:project_id>")
def update_project(project_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    project = owned_project(project_id, user.id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = str(data["name"]).strip()
        if not name or len(name) > 120:
            return jsonify({"error": "Project name is required and must be under 120 characters."}), 400
        project.name = name
    if "description" in data:
        description = str(data["description"])
        if len(description) > 3000:
            return jsonify({"error": "Project description is too long."}), 400
        project.description = description
    if "goals" in data:
        goals = str(data["goals"])
        if len(goals) > 2000:
            return jsonify({"error": "Project goals are too long."}), 400
        project.goals = goals
    if "tech_stack" in data:
        stack = data["tech_stack"]
        if not isinstance(stack, list) or len(stack) > 20 or any(not isinstance(x, str) for x in stack):
            return jsonify({"error": "tech_stack must be a list of up to 20 strings."}), 400
        project.tech_stack = ", ".join(part.strip()[:40] for part in stack if part.strip())
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"project": project.to_dict(include_files=True)})


@bp.delete("/<int:project_id>")
def delete_project(project_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    project = owned_project(project_id, user.id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/<int:project_id>/files")
@limiter.limit("30 per hour")
def add_project_file(project_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    project = owned_project(project_id, user.id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    data = request.get_json(silent=True) or {}
    path = _normalise_path(data.get("path", ""))
    content = data.get("content")
    if not path:
        return jsonify({"error": "Use a relative project path without '..' segments or drive prefixes."}), 400
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "File content must be non-empty UTF-8 text."}), 400
    if len(content) > current_app.config["MAX_PROJECT_FILE_CHARS"]:
        return jsonify({"error": "File exceeds the configured character limit."}), 413
    basename = path.rsplit("/", 1)[-1].lower()
    extension = ".env.example" if basename.endswith(".env.example") else (
        "." + basename.rsplit(".", 1)[-1] if "." in basename else ""
    )
    language = ALLOWED_EXTENSIONS.get(extension)
    if not language:
        return jsonify({"error": "Unsupported file type. Add source code or text files only."}), 415

    existing = ProjectFile.query.filter_by(project_id=project.id, path=path).first()
    total_chars = db.session.query(func.coalesce(func.sum(ProjectFile.character_count), 0)).filter(
        ProjectFile.project_id == project.id
    ).scalar()
    current_chars = existing.character_count if existing else 0
    if total_chars - current_chars + len(content) > current_app.config["MAX_PROJECT_TOTAL_CHARS"]:
        return jsonify({"error": "Project context storage limit reached."}), 413
    if not existing and ProjectFile.query.filter_by(project_id=project.id).count() >= current_app.config["MAX_PROJECT_FILES"]:
        return jsonify({"error": "Project file limit reached."}), 429

    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if existing:
        existing.content = content
        existing.language = language
        existing.sha256 = digest
        existing.character_count = len(content)
        existing.updated_at = datetime.now(timezone.utc)
        project_file = existing
    else:
        project_file = ProjectFile(
            project_id=project.id, path=path, language=language, content=content,
            sha256=digest, character_count=len(content),
        )
        db.session.add(project_file)
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"file": project_file.to_dict()}), 201


@bp.delete("/<int:project_id>/files/<int:file_id>")
def delete_project_file(project_id: int, file_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    project = owned_project(project_id, user.id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    project_file = ProjectFile.query.filter_by(id=file_id, project_id=project.id).first()
    if not project_file:
        return jsonify({"error": "Project file not found."}), 404
    db.session.delete(project_file)
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"ok": True})
