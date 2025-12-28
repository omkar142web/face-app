from flask import Flask, render_template, request, redirect, jsonify
from deepface import DeepFace
import numpy as np
import os
import cv2
import uuid

from database import init_db, insert_face, get_all_faces

from flask import send_from_directory


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["FACE_FOLDER"] = "faces"

@app.route('/faces/<path:filename>')
def serve_faces(filename):
    return send_from_directory('faces', filename)

init_db()

def extract_embedding(image_path):
    try:
        obj = DeepFace.represent(img_path=image_path, model_name="Facenet")
        return obj[0]["embedding"]
    except Exception as e:
        print("Embedding Error:", e)
        return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add-face", methods=["POST"])
def add_face():
    name = request.form.get("name", "Unknown")

    file = request.files["image"]
    if not file:
        return "No File", 400

    filename = str(uuid.uuid4()) + ".jpg"
    path = os.path.join(app.config["FACE_FOLDER"], filename)
    file.save(path)

    embedding = extract_embedding(path)
    if not embedding:
        return "Face not detected", 400

    insert_face(name, path, embedding)

    return "Face Stored Successfully 👍"


@app.route("/search")
def search_page():
    return render_template("search.html")


@app.route("/find", methods=["POST"])
def find_match():
    file = request.files["image"]
    if not file:
        return jsonify({"match": False, "message": "No file"}), 400

    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], "query.jpg")
    file.save(temp_path)

    query_embedding = extract_embedding(temp_path)
    if not query_embedding:
        return jsonify({"match": False, "message": "No face detected"}), 400

    faces = get_all_faces()
    if not faces:
        return jsonify({"match": False, "message": "Database empty"}), 404

    results = []

    for fid, name, image_path, embedding in faces:
        emb = np.array(eval(embedding))

        score = np.dot(query_embedding, emb) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(emb)
        )

        confidence = float(max(0, min(1, score))) * 100

        results.append({
            "name": name,
            "image": image_path,
            "confidence": round(confidence, 2)
        })

    # ------------------------------------
    # 🔥 NEW PART — GROUP BY PERSON (BEST HIT)
    # ------------------------------------
    best = {}
    for r in results:
        if r["name"] not in best or r["confidence"] > best[r["name"]]["confidence"]:
            best[r["name"]] = r

    results = list(best.values())
    results.sort(key=lambda x: x["confidence"], reverse=True)

    top = results[:5]

    return jsonify({
        "match": True if top and top[0]["confidence"] > 70 else False,
        "results": top
    })


    

if __name__ == "__main__":
    app.run(debug=True)
