from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db
from app.forms import RegisterForm, LoginForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


def _is_safe_next(target):
    # Only allow redirects to paths inside this site.
    return bool(target) and target.startswith("/") and not target.startswith("//")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=form)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)
        login_user(user)
        next_page = request.args.get("next")
        if _is_safe_next(next_page):
            return redirect(next_page)
        return redirect(url_for("dashboard.index"))
    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))