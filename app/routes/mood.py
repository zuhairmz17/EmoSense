from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.forms import MoodForm
from app.models import MoodEntry

mood_bp = Blueprint("mood", __name__, url_prefix="/mood")

PER_PAGE = 10


def _get_own_entry_or_404(entry_id):
    # Filtering by user_id means other users' entries return 404.
    return MoodEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()


@mood_bp.route("/", methods=["GET", "POST"])
@login_required
def tracker():
    form = MoodForm()
    if form.validate_on_submit():
        note = (form.note.data or "").strip() or None
        entry = MoodEntry(
            user_id=current_user.id,
            mood=form.mood.data,
            intensity=form.intensity.data,
            note=note,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Mood entry saved.", "success")
        return redirect(url_for("mood.tracker"))

    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(
        db.select(MoodEntry)
        .filter_by(user_id=current_user.id)
        .order_by(MoodEntry.created_at.desc()),
        page=page,
        per_page=PER_PAGE,
        error_out=False,
    )
    return render_template("mood_tracker.html", form=form, pagination=pagination)


@mood_bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit(entry_id):
    entry = _get_own_entry_or_404(entry_id)
    form = MoodForm(obj=entry)
    if form.validate_on_submit():
        entry.mood = form.mood.data
        entry.intensity = form.intensity.data
        entry.note = (form.note.data or "").strip() or None
        db.session.commit()
        flash("Mood entry updated.", "success")
        return redirect(url_for("mood.tracker"))
    return render_template("mood_edit.html", form=form, entry=entry)


@mood_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = _get_own_entry_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Mood entry deleted.", "info")
    return redirect(url_for("mood.tracker"))