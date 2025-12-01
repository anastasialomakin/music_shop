import pytest
from app import create_app, db
from config import TestConfig

@pytest.fixture()
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        # ТЕСТАМ seed не нужен, тесты сами создают то, что надо
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
