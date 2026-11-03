from fastapi.testclient import TestClient
import app.main as m
import app.auth as auth

anon = TestClient(m.app)
ADMIN = {"X-Admin-Key": "test-admin"}

def test_no_key_rejected():
    assert anon.post("/scan", json={"prompt": "hi"}).status_code == 401

def test_wrong_key_rejected():
    r = anon.post("/scan", json={"prompt": "hi"}, headers={"X-API-Key": "ps_nope"})
    assert r.status_code == 401

def test_valid_key_works():
    key = auth.create_key("t")
    r = anon.post("/scan", json={"prompt": "What is 2+2?"}, headers={"X-API-Key": key})
    assert r.status_code == 200 and r.json()["safe"] is True

def test_revoked_key_rejected():
    key = auth.create_key("t")
    auth.revoke_key(auth.list_keys()[0]["id"])
    assert anon.post("/scan", json={"prompt": "hi"}, headers={"X-API-Key": key}).status_code == 401

def test_rate_limit(monkeypatch):
    monkeypatch.setattr(auth, "RATE_LIMIT", 3)
    h = {"X-API-Key": auth.create_key("t")}
    codes = [anon.post("/scan", json={"prompt": "hi"}, headers=h).status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]

def test_rate_limit_is_per_key(monkeypatch):
    monkeypatch.setattr(auth, "RATE_LIMIT", 1)
    a, b = {"X-API-Key": auth.create_key("a")}, {"X-API-Key": auth.create_key("b")}
    assert anon.post("/scan", json={"prompt": "hi"}, headers=a).status_code == 200
    assert anon.post("/scan", json={"prompt": "hi"}, headers=b).status_code == 200

def test_logs_need_admin_key():
    assert anon.get("/logs").status_code == 401
    assert anon.get("/logs", headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert anon.get("/logs", headers=ADMIN).status_code == 200

def test_api_key_is_not_an_admin_key():
    key = auth.create_key("t")
    assert anon.get("/stats", headers={"X-API-Key": key}).status_code == 401

def test_admin_disabled_without_env(monkeypatch):
    monkeypatch.delenv("ADMIN_KEY")
    assert anon.get("/logs", headers=ADMIN).status_code == 503

def test_oversized_prompt_rejected():
    key = auth.create_key("t")
    r = anon.post("/scan", json={"prompt": "a" * 20001}, headers={"X-API-Key": key})
    assert r.status_code == 422