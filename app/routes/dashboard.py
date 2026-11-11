from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import MoodEntry

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    mood_count = current_user.mood_entries.count()
    recent = (
        current_user.mood_entries.order_by(MoodEntry.created_at.desc()).limit(5).all()
    )
    return render_template("dashboard.html", mood_count=mood_count, recent=recent)