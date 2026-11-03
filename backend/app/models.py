from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_language = db.Column(db.String(8), nullable=False, default="en")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    conversations = db.relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    projects = db.relationship("Project", back_populates="user", cascade="all, delete-orphan")
    learning_profile = db.relationship(
        "LearningProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "preferred_language": self.preferred_language,
            "created_at": self.created_at.isoformat(),
        }


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(180), nullable=False, default="New conversation")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    user = db.relationship("User", back_populates="conversations")
    messages = db.relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    documents = db.relationship(
        "Document", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Document.created_at",
    )


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(120))
    input_characters = db.Column(db.Integer)
    output_characters = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    conversation = db.relationship("Conversation", back_populates="messages")
    sources = db.relationship(
        "MessageSource", back_populates="message", cascade="all, delete-orphan",
        order_by="MessageSource.id",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "sources": [source.to_dict() for source in self.sources],
            "created_at": self.created_at.isoformat(),
        }


class MessageSource(db.Model):
    __tablename__ = "message_sources"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(
        db.Integer, db.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id = db.Column(
        db.Integer, db.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    ref_id = db.Column(db.String(12), nullable=False)
    kind = db.Column(db.String(20), nullable=False)
    label = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(2048))
    page_number = db.Column(db.Integer)

    message = db.relationship("Message", back_populates="sources")

    def to_dict(self):
        return {
            "id": self.ref_id,
            "kind": self.kind,
            "label": self.label,
            "url": self.url,
            "page": self.page_number,
        }


class Document(db.Model):
    """Legacy document metadata table retained for forward-compatible migrations."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = db.Column(db.String(180), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    page_count = db.Column(db.Integer, nullable=False)
    character_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    conversation = db.relationship("Conversation", back_populates="documents")
    pages = db.relationship(
        "DocumentPage", back_populates="document", cascade="all, delete-orphan",
        order_by="DocumentPage.page_number",
    )


class DocumentPage(db.Model):
    __tablename__ = "document_pages"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    document = db.relationship("Document", back_populates="pages")

    __table_args__ = (
        db.UniqueConstraint("document_id", "page_number", name="uq_document_page_number"),
    )


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    goals = db.Column(db.Text, nullable=False, default="")
    tech_stack = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    user = db.relationship("User", back_populates="projects")
    files = db.relationship(
        "ProjectFile", back_populates="project", cascade="all, delete-orphan",
        order_by="ProjectFile.path",
    )

    def to_dict(self, include_files=False):
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "goals": self.goals,
            "tech_stack": [part.strip() for part in self.tech_stack.split(",") if part.strip()],
            "file_count": len(self.files),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_files:
            result["files"] = [item.to_dict() for item in self.files]
        return result


class ProjectFile(db.Model):
    __tablename__ = "project_files"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    path = db.Column(db.String(240), nullable=False)
    language = db.Column(db.String(32), nullable=False, default="text")
    content = db.Column(db.Text, nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    character_count = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    project = db.relationship("Project", back_populates="files")

    __table_args__ = (
        db.UniqueConstraint("project_id", "path", name="uq_project_file_path"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "path": self.path,
            "language": self.language,
            "character_count": self.character_count,
            "updated_at": self.updated_at.isoformat(),
        }


class ConversationWorkspace(db.Model):
    __tablename__ = "conversation_workspaces"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    mode = db.Column(db.String(20), nullable=False, default="teach")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        db.CheckConstraint("mode IN ('teach', 'build', 'review')", name="ck_workspace_mode"),
    )


class KnowledgeArticle(db.Model):
    __tablename__ = "knowledge_articles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=False, default="")
    tags = db.Column(db.String(500), nullable=False, default="")
    language = db.Column(db.String(12), nullable=False, default="en")
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(2048))
    is_published = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "category": self.category,
            "summary": self.summary,
            "tags": [part.strip() for part in self.tags.split(",") if part.strip()],
            "language": self.language,
            "source_url": self.source_url,
            "updated_at": self.updated_at.isoformat(),
        }


class LearningProfile(db.Model):
    __tablename__ = "learning_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    experience_level = db.Column(db.String(20), nullable=False, default="beginner")
    preferred_language = db.Column(db.String(12), nullable=False, default="auto")
    learning_goals = db.Column(db.Text, nullable=False, default="")
    teaching_style = db.Column(db.String(30), nullable=False, default="step-by-step")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="learning_profile")

    def to_dict(self):
        return {
            "experience_level": self.experience_level,
            "preferred_language": self.preferred_language,
            "learning_goals": self.learning_goals,
            "teaching_style": self.teaching_style,
            "updated_at": self.updated_at.isoformat(),
        }


class UsageEvent(db.Model):
    __tablename__ = "usage_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="SET NULL"))
    model = db.Column(db.String(120), nullable=False)
    input_characters = db.Column(db.Integer, nullable=False, default=0)
    output_characters = db.Column(db.Integer, nullable=False, default=0)
    input_tokens = db.Column(db.Integer)
    output_tokens = db.Column(db.Integer)
    latency_ms = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False, default="completed")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
