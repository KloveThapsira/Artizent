import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).resolve().parent / "autodeploy.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT UNIQUE,
        project_name TEXT,
        framework TEXT,
        language TEXT,
        project_type TEXT,
        platform TEXT,
        build_command TEXT,
        output_folder TEXT,
        status TEXT,
        live_url TEXT,
        logs TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def upsert_deployment(data: dict):
    conn = get_conn()
    existing = conn.execute("SELECT id FROM deployments WHERE project_id=?", (data["project_id"],)).fetchone()
    if existing:
        fields = [k for k in data.keys() if k != "project_id"]
        sql = ", ".join([f"{k}=?" for k in fields])
        conn.execute(f"UPDATE deployments SET {sql} WHERE project_id=?", [data[k] for k in fields] + [data["project_id"]])
    else:
        data.setdefault("created_at", datetime.utcnow().isoformat())
        keys = list(data.keys())
        conn.execute(
            f"INSERT INTO deployments ({','.join(keys)}) VALUES ({','.join(['?']*len(keys))})",
            [data[k] for k in keys],
        )
    conn.commit()
    conn.close()

def get_deployment(project_id: str):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM deployments WHERE project_id=?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
