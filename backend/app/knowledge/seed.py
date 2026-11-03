from ..extensions import db
from ..models import KnowledgeArticle

ARTICLES = [
    {
        "slug": "python-debugging",
        "title": "A reliable workflow for debugging Python",
        "category": "Python",
        "summary": "Read tracebacks, isolate a minimal reproduction, inspect state, and write a regression test.",
        "tags": "python,debugging,traceback,testing,exceptions",
        "content": """# Python debugging workflow

1. Read the final line of the traceback first. It normally names the exception type and message.
2. Read upward to find the first frame in your own code. The final failing line may be inside a library, while your call site explains why it was called.
3. Reproduce the error with the smallest input and the fewest moving parts.
4. Inspect the values and types at the failing boundary. Check None values, empty collections, string/number conversions, file paths, and environment variables.
5. Form one hypothesis and test it. Avoid changing several unrelated lines at once.
6. Add a regression test that fails before the fix and passes after it.
7. Explain the root cause separately from the code change.

Common examples:
- AttributeError: inspect the actual object and whether it can be None.
- KeyError: check the key and the input schema; use explicit validation rather than silently hiding missing data.
- TypeError: inspect types and function signatures at the boundary.
- ImportError: verify the active virtual environment, package name, and working directory.

Do not execute untrusted code copied from an error message or issue. A traceback is evidence, not a complete explanation.""",
    },
    {
        "slug": "web-app-architecture",
        "title": "Understand a full-stack web application",
        "category": "Web Development",
        "summary": "How the browser, API, business logic, database, authentication, and tests fit together.",
        "tags": "web,frontend,backend,react,flask,api,http,architecture",
        "content": """# Full-stack web application fundamentals

A browser UI renders information and gathers user input. It should not contain private server credentials or database passwords.
The frontend communicates with a backend using HTTP requests. An API endpoint validates the request, checks authentication and authorisation, runs business logic, and returns a structured response.
The backend is responsible for enforcing permissions; hiding a button in React is not access control.
A relational database stores durable records. Use primary keys, foreign keys, unique constraints, indexes for frequently queried columns, and transactions for related writes.
Authentication proves who a user is. Authorisation decides what that user may access. Every object lookup must enforce ownership or a role-based permission.
Separate layers by responsibility: route/controller, service/business logic, persistence model, and external provider adapters.
Test the API independently from the UI. Test normal cases, invalid input, unauthenticated requests, cross-user access, and external service failures.
For production, use HTTPS, secure cookies, CSRF protection when using cookie sessions, request limits, structured logs, backups, migrations, and monitoring.""",
    },
    {
        "slug": "sql-data-modeling",
        "title": "Practical relational database design",
        "category": "Databases",
        "summary": "Model entities, relationships, constraints, indexes, and safe transactions.",
        "tags": "sql,mysql,database,schema,normalization,index,transaction",
        "content": """# Relational database design

Start by identifying entities and the rules between them. For example, one user can own many projects; one project can contain many project files.
Give each entity a stable primary key. Use foreign keys to express relationships and choose delete behaviour deliberately.
Add unique constraints for values that must not duplicate, such as a username or a file path within one project.
Normalise repeated data into related tables to avoid update anomalies. Store a list in a separate table when each item needs its own identity or query behaviour.
Add an index to columns used frequently for filtering, joining, and ordering. Indexes improve reads but add storage and write cost.
Use transactions when multiple writes must succeed or fail together. Never build SQL statements by concatenating untrusted user input; use parameterised queries or an ORM.
For a schema change on an existing database, use migrations. Creating missing tables does not add columns or safely transform existing records.""",
    },
    {
        "slug": "machine-learning-workflow",
        "title": "A dependable machine-learning workflow",
        "category": "AI and Machine Learning",
        "summary": "From a clear target and baseline to data splits, evaluation, leakage checks, and deployment.",
        "tags": "ai,machine-learning,ml,data,training,evaluation,scikit-learn",
        "content": """# Machine-learning project workflow

1. Define the prediction target and the decision the model is meant to support.
2. Inspect the data: provenance, permission, missing values, class balance, duplicates, and possible sensitive fields.
3. Create training, validation, and held-out test sets before tuning. For time-dependent data, split chronologically. For related users or entities, consider group-based splitting.
4. Build a simple baseline. A complex neural network is not automatically better than a baseline.
5. Fit preprocessing steps on training data only. Fitting scalers, imputers, feature selection, or encoders on the full dataset can leak information.
6. Choose metrics aligned with the problem. Accuracy can hide poor minority-class performance; consider precision, recall, F1, ROC-AUC, PR-AUC, or calibration where appropriate.
7. Compare on validation data, then evaluate once on the held-out test set.
8. Inspect errors, robustness, fairness, and drift before deployment.
9. Version the data, code, model, configuration, and evaluation report.

A model prediction is not proof of causation. Explain uncertainty and limitations to users.""",
    },
    {
        "slug": "deep-learning-foundations",
        "title": "Deep-learning foundations without magic",
        "category": "Deep Learning",
        "summary": "Tensors, layers, forward passes, loss, gradients, optimisation, and honest evaluation.",
        "tags": "deep-learning,neural-network,pytorch,backpropagation,tensor,gradient",
        "content": """# Deep-learning foundations

A neural network maps input tensors to outputs through parameterised operations called layers.
A forward pass computes predictions. A loss function measures how predictions differ from the target.
Backpropagation applies the chain rule to compute gradients of the loss with respect to parameters.
An optimiser such as SGD or Adam updates parameters using those gradients.
Training data updates model parameters. Validation data helps select settings and detect overfitting. A separate test set estimates final generalisation.
Start with a tiny model and a small batch. Check tensor shapes, output ranges, loss values, and whether gradients are finite and nonzero.
If loss does not decrease, inspect labels, preprocessing, learning rate, loss function, output activation, and gradient flow.
GPU acceleration changes speed, not the correctness of the learning process. For small experiments, a CPU is often sufficient.
Never claim a model is useful based only on training loss. Compare to a baseline and report performance on held-out examples.""",
    },
    {
        "slug": "secure-code-review",
        "title": "A practical secure-code review checklist",
        "category": "Software Security",
        "summary": "Review trust boundaries, validation, authentication, authorisation, secrets, dependencies, and tests.",
        "tags": "security,owasp,code-review,authentication,authorization,xss,sql-injection",
        "content": """# Secure-code review checklist

- Identify trust boundaries: browser input, uploaded files, third-party API responses, environment variables, and database records.
- Validate input on the server with type, length, and allowed-value checks.
- Use parameterised database operations. Never interpolate untrusted input into SQL.
- Encode output for its destination context. Avoid rendering untrusted HTML. Review XSS sinks and URL schemes.
- Authenticate users and enforce object-level authorisation on every read, update, and delete.
- Keep secrets out of source code, browser bundles, logs, and error messages.
- Limit upload size and file types; treat file contents as untrusted and isolate risky parsers.
- Add rate limits, timeouts, request-size limits, and safe error handling.
- Pin and review dependencies; remove unused packages.
- Test unauthenticated access, cross-user access, malformed data, and abuse cases.

Only test systems you own or have explicit permission to assess. A review finding should include impact, evidence, safe reproduction steps, and a remediation suggestion.""",
    },
]


def seed_knowledge_base():
    """Insert missing, versioned starter articles without overwriting administrator edits."""
    created = 0
    for article in ARTICLES:
        if KnowledgeArticle.query.filter_by(slug=article["slug"]).first():
            continue
        db.session.add(KnowledgeArticle(**article, language="en", is_published=True))
        created += 1
    if created:
        db.session.commit()
    return created
