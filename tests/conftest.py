import pytest
from app import db, auth

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    auth._hits.clear()                 # rate-limit counters must not leak between tests
    monkeypatch.setenv("ADMIN_KEY", "test-admin")