import pytest
from app import create_app, db
from app.models import User

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

@pytest.fixture
def seeded_app(app):
    from app.seed_db import seed_database
    with app.app_context():
        seed_database()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    u = User(username='testuser', email='test@example.com')
    u.set_password('1234')
    db.session.add(u)
    db.session.commit()
    return u
