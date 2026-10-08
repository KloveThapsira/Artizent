import sqlite3
from pathlib import Path
import json

db = Path(__file__).resolve().parents[1] / 'database' / 'autodeploy.db'
if not db.exists():
    print('DB not found at', db)
    raise SystemExit(1)
conn = sqlite3.connect(str(db))
cur = conn.cursor()
cur.execute('SELECT project_id,status,live_url,substr(logs,1,200) FROM deployments ORDER BY id DESC LIMIT 10')
rows = cur.fetchall()
for r in rows:
    print(json.dumps(r))
conn.close()
