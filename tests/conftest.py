import pytest

from app import app as flask_app
from database.db import init_db


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    monkeypatch.setattr("database.db.DB_PATH", path)
    init_db(path)
    return path


@pytest.fixture
def app(db_path):
    flask_app.config.update(TESTING=True)
    yield flask_app
