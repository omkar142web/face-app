import sqlite3
import json
import os

# Database file name
DB = "models.db"


def init_db():
    """
    Create database and faces table if they do not exist
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_path TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def insert_face(name, image_path, embedding):
    """
    Insert a face record into database
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "INSERT INTO faces (name, image_path, embedding) VALUES (?, ?, ?)",
        (name, image_path, json.dumps(embedding))
    )

    conn.commit()
    conn.close()


def get_all_faces():
    """
    Return all face records
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT id, name, image_path, embedding FROM faces")
    rows = c.fetchall()

    conn.close()
    return rows


def delete_person(name):
    """
    Delete all faces of a person
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM faces WHERE name = ?", (name,))

    conn.commit()
    conn.close()


def delete_face(image_path):
    """
    Delete a single face by image path
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM faces WHERE image_path = ?", (image_path,))

    conn.commit()
    conn.close()
