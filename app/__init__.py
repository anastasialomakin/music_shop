from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models
from app.seed_db import seed_database

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

# ----------------------------
# Автоматическое наполнение БД только если нет админа
# ----------------------------
with app.app_context():
    db.create_all()
    seed_database()
