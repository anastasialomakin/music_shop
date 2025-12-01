from flask import Flask
from config import Config, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == "testing":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # импорт маршрутов делаем ПОСЛЕ создания app
    import app.routes
    import app.models

    return app


# Глобальный app — как у тебя раньше!
app = create_app()


@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))


def setup_database(app):
    from app.seed_db import seed_database
    with app.app_context():
        db.create_all()
        seed_database()
