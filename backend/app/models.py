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

    def to_list_dict(self):
        last_message = self.messages[-1] if self.messages else None
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_message_preview": (last_message.content[:100] if last_message else ""),
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "page_count": self.page_count,
            "character_count": self.character_count,
            "created_at": self.created_at.isoformat(),
        }


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
