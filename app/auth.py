import hashlib, os, secrets, time
from collections import defaultdict, deque
from fastapi import Header, HTTPException
from .db import conn

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "30"))   # requests per window, per key
WINDOW = 60                                       # seconds
_hits: dict[str, deque] = defaultdict(deque)      # in memory: resets on restart

def _hash(k: str) -> str:
    return hashlib.sha256(k.encode()).hexdigest()

def create_key(name: str) -> str:
    key = "ps_" + secrets.token_urlsafe(24)
    with conn() as c:
        c.execute("INSERT INTO api_keys (key_hash, name, created) VALUES (?,?,?)",
                  (_hash(key), name, time.time()))
    return key                                    # shown once, never stored in plain text

def list_keys():
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT id, name, created, active FROM api_keys ORDER BY id")]

def revoke_key(key_id: int) -> bool:
    with conn() as c:
        return c.execute("UPDATE api_keys SET active = 0 WHERE id = ?", (key_id,)).rowcount > 0

def require_key(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(401, "Missing X-API-Key header")
    h = _hash(x_api_key)
    with conn() as c:
        row = c.execute("SELECT id FROM api_keys WHERE key_hash = ? AND active = 1", (h,)).fetchone()
    if not row:
        raise HTTPException(401, "Invalid or revoked API key")

    now, q = time.time(), _hits[h]
    while q and q[0] <= now - WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        retry = max(1, int(WINDOW - (now - q[0])))
        raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry)})
    q.append(now)
    return h

def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    admin = os.getenv("ADMIN_KEY")
    if not admin:
        raise HTTPException(503, "Admin access disabled: ADMIN_KEY is not set")   # fail closed
    if not x_admin_key or not secrets.compare_digest(x_admin_key, admin):
        raise HTTPException(401, "Invalid admin key")