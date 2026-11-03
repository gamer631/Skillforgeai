from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from ..auth.routes import current_user
from ..extensions import db
from ..models import LearningProfile

bp = Blueprint("profile", __name__, url_prefix="/api/profile")

EXPERIENCE_LEVELS = {"beginner", "intermediate", "advanced"}
LANGUAGES = {"auto", "en", "ne"}
TEACHING_STYLES = {"step-by-step", "concise", "socratic", "hands-on"}


@bp.get("")
def get_profile():
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    profile = LearningProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = LearningProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
    return jsonify({"profile": profile.to_dict()})


@bp.put("")
def update_profile():
    user = current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
    data = request.get_json(silent=True) or {}
    profile = LearningProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = LearningProfile(user_id=user.id)
        db.session.add(profile)
    experience = data.get("experience_level", profile.experience_level)
    language = data.get("preferred_language", profile.preferred_language)
    style = data.get("teaching_style", profile.teaching_style)
    goals = data.get("learning_goals", profile.learning_goals)
    if not isinstance(experience, str) or experience not in EXPERIENCE_LEVELS:
        return jsonify({"error": "Choose a supported experience level, language, and teaching style."}), 400
    if not isinstance(language, str) or language not in LANGUAGES:
        return jsonify({"error": "Choose a supported experience level, language, and teaching style."}), 400
    if not isinstance(style, str) or style not in TEACHING_STYLES:
        return jsonify({"error": "Choose a supported experience level, language, and teaching style."}), 400
    if not isinstance(goals, str) or len(goals) > 2000:
        return jsonify({"error": "Learning goals must be text under 2,000 characters."}), 400
    profile.experience_level = experience
    profile.preferred_language = language
    profile.teaching_style = style
    profile.learning_goals = goals.strip()
    profile.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"profile": profile.to_dict()})
