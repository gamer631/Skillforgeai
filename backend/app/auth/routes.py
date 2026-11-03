from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request, session

from ..extensions import db, limiter
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if user is None or not user.is_active:
        session.clear()
        return None
    return user


@bp.get("/me")
def me():
    user = current_user()
    return jsonify({"user": user.to_dict() if user else None})


@bp.post("/register")
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    display_name = str(data.get("display_name", "")).strip()
    password = str(data.get("password", ""))

    if not email or not display_name or len(display_name) > 100:
        return jsonify({"error": "Enter your name and a valid email address."}), 400
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return jsonify({"error": "Enter a valid email address."}), 400
    if len(password) < 10:
        return jsonify({"error": "Use a password with at least 10 characters."}), 400
    if len(password) > 128:
        return jsonify({"error": "Password is too long."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists."}), 409

    user = User(email=email, display_name=display_name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"user": user.to_dict()}), 201


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user = User.query.filter_by(email=email).first()
    if not user or not user.is_active or not user.check_password(password):
        return jsonify({"error": "Email or password is incorrect."}), 401
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"user": user.to_dict()})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})
