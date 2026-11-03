from types import SimpleNamespace

from app.knowledge.engine import retrieve_context, split_chunks, terms


def test_retrieval_ranks_relevant_project_file_and_shared_guide():
    articles = [
        SimpleNamespace(
            slug="python-debugging", title="Python debugging", summary="Tracebacks and exceptions",
            tags="python,debugging,traceback", content="Read the traceback and find the first failing line.",
        ),
        SimpleNamespace(
            slug="machine-learning", title="Machine learning", summary="Model training",
            tags="ml,training", content="Split data before fitting model parameters.",
        ),
    ]
    files = [
        SimpleNamespace(path="backend/auth.py", content="def authenticate(user):\n    if user is None:\n        raise PermissionError()\n"),
        SimpleNamespace(path="frontend/App.jsx", content="export default function App() { return null; }"),
    ]
    context, sources = retrieve_context(
        "Why does my Python authentication function raise PermissionError?",
        articles, files, max_chunks=4,
    )
    assert "traceback" in context.lower() or "first failing line" in context.lower()
    assert "backend/auth.py" in context
    assert any(item["kind"] == "knowledge" for item in sources)
    assert any(item["kind"] == "project" for item in sources)


def test_retrieval_limits_context_and_handles_empty_corpus():
    context, sources = retrieve_context("anything", [], [])
    assert context == ""
    assert sources == []
    chunks = split_chunks("A" * 5000, max_chars=1000, overlap=100)
    assert len(chunks) > 1
    assert all(len(item) <= 1000 for item in chunks)


def test_terms_keep_code_identifiers_and_filter_common_words():
    result = terms("Explain the Flask API and SQLAlchemy relationship")
    assert "flask" in result
    assert "sqlalchemy" in result
    assert "explain" not in result
