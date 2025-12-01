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

    # Конфиг выбирает pipeline
    if config_name == "testing":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import routes, models
    return app


# Используется приложением
app = create_app()


# ✨ ЭТУ ФУНКЦИЮ ВЫЗЫВАЕТ TEAMCITY ✨
def setup_database(app):
    with app.app_context():
        db.create_all()
        from app.seed_db import seed_database
        seed_database()
