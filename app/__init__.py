from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import routes, models

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    # ---------------------------------------
    # Автоматическое создание БД + сид
    # Но ТОЛЬКО если не в режиме тестов
    # ---------------------------------------
    if not app.config.get("TESTING", False):
        from app.seed_db import seed_database
        with app.app_context():
            db.create_all()
            seed_database()

    return app
