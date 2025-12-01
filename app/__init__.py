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

# импорт моделей (они не импортируют app, поэтому цикл НЕ возникает)
from app import models

@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

def setup_database():
    from app.seed_db import seed_database
    with app.app_context():
        db.create_all()
        seed_database()

# ИМПОРТ ROUTES САМЫЙ ПОСЛЕДНИЙ
from app import routes
