import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Optional,
)

from app.constants import MOOD_EMOJI
from app.models import User


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_email(self, field):
        email = field.data.strip().lower()
        if User.query.filter_by(email=email).first():
            raise ValidationError("An account with this email already exists.")

    def validate_password(self, field):
        pw = field.data or ""
        if not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
            raise ValidationError("Password must contain at least one letter and one number.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class MoodForm(FlaskForm):
    mood = RadioField(
        "How are you feeling?",
        choices=[(name, f"{emoji} {name}") for name, emoji in MOOD_EMOJI.items()],
        validate_choice=False,
    )
    intensity = RadioField(
        "Intensity (1 = very mild, 5 = very strong)",
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        default=3,
        validate_choice=False,
    )
    note = TextAreaField("Journal note (optional)", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save entry")

    def validate_mood(self, field):
        if field.data not in MOOD_EMOJI:
            raise ValidationError("Please select a mood.")

    def validate_intensity(self, field):
        if field.data not in (1, 2, 3, 4, 5):
            raise ValidationError("Please choose an intensity from 1 to 5.")