import sqlite3, json
conn=sqlite3.connect('backend/database/autodeploy.db')
cur=conn.cursor()
cur.execute("SELECT project_id, live_url, status FROM deployments WHERE live_url LIKE '%source-%' OR live_url LIKE '%source_%'")
rows=cur.fetchall()
print(json.dumps(rows, indent=2))
conn.close()
