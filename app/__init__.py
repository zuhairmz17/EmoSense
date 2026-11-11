import os
from datetime import timezone, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    if config_name == "production" and not os.environ.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in production.")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401  (registers the tables)
    from app.constants import MOOD_EMOJI
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.mood import mood_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(mood_bp)

    app.jinja_env.globals["MOOD_EMOJI"] = MOOD_EMOJI

    @app.template_filter("localtime")
    def localtime(value, fmt="%d %b %Y, %I:%M %p"):
        if value is None:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        offset = timezone(timedelta(minutes=app.config["DISPLAY_UTC_OFFSET_MINUTES"]))
        return value.astimezone(offset).strftime(fmt)

    with app.app_context():
        db.create_all()
        from app.seed import seed_questions
        seed_questions()

    return app