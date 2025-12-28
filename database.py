import sqlite3
import json

DB = "models.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image_path TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_face(name, image_path, embedding):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO faces (name, image_path, embedding) VALUES (?, ?, ?)",
              (name, image_path, json.dumps(embedding)))
    conn.commit()
    conn.close()

def get_all_faces():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, image_path, embedding FROM faces")
    rows = c.fetchall()
    conn.close()
    return rows
