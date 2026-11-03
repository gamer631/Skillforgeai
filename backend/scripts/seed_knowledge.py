from app import create_app
from app.config import Config
from app.extensions import db
from app.knowledge.seed import seed_knowledge_base

app = create_app(Config, provider=None)
with app.app_context():
    inserted = seed_knowledge_base()
    total = db.session.query(db.func.count()).select_from(__import__("app.models", fromlist=["KnowledgeArticle"]).KnowledgeArticle).scalar()
    print(f"Inserted {inserted} starter articles; {total} published knowledge articles are available.")
