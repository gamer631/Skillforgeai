from flask import Blueprint, jsonify, request

from ..auth.routes import current_user
from ..models import KnowledgeArticle

bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")


@bp.get("")
def list_knowledge():
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    query = str(request.args.get("q", "")).strip().lower()
    articles = KnowledgeArticle.query.filter_by(is_published=True).order_by(
        KnowledgeArticle.category, KnowledgeArticle.title
    ).all()
    if query:
        articles = [
            item for item in articles
            if query in item.title.lower()
            or query in item.category.lower()
            or query in item.summary.lower()
            or query in item.tags.lower()
        ]
    return jsonify({"articles": [item.to_dict() for item in articles]})
