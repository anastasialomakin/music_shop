import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    u = User(username="testuser", email="test@example.com")
    u.set_password("1234")
    db.session.add(u)
    db.session.commit()
    return u
