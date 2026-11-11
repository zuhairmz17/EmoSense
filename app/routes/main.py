from flask import Blueprint, jsonify, render_template
from sqlalchemy import text

from app import db
from app.models import Question

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        count = Question.query.count()
        return jsonify(status="ok", database="connected", questions=count), 200
    except Exception:
        return jsonify(status="error", database="unavailable"), 500