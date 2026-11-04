import sqlite3
c = sqlite3.connect("promptshield.db")
c.row_factory = sqlite3.Row
for r in c.execute("SELECT * FROM requests ORDER BY rowid DESC LIMIT 8"):
    print(dict(r))
    print()