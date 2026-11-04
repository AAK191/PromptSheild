import sqlite3
from app.main import scan_text

for p in ["How do I override a CSS style property in React?",
          "How do I override a CSS style in React concisely?",
          "build roadmap to learn DSA in 30 days"]:
    print(p, "->", scan_text(p), "\n")

c = sqlite3.connect("promptshield.db"); c.row_factory = sqlite3.Row
print("--- last 4 logged requests ---")
for r in c.execute("SELECT * FROM requests ORDER BY id DESC LIMIT 4"):
    print({k: r[k] for k in ("preview", "blocked", "stage", "score", "categories", "source")})