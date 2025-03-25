from flask import Flask, request, jsonify
from pymongo import MongoClient
import hashlib
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

# MongoDB connection (Replace <db_password> with actual password)
MONGO_URI = "mongodb+srv://dacyberman:qwerty123@sw.gfemx.mongodb.net/?retryWrites=true&w=majority&appName=SW"
client = MongoClient(MONGO_URI)
db = client["dke"]  # Replace with your database name
collection = db["docx_metadata"]  # Replace with your collection name

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if not exists

@app.route("/")
def home():
    return "MongoDB connected successfully!"

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Compute file hash (SHA-256)
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    file_hash = hasher.hexdigest()

    # Store info in MongoDB
    file_info = {
        "filename": file.filename,
        "hash": file_hash,
        "upload_date": datetime.utcnow()
    }
    collection.insert_one(file_info)

    return jsonify({"message": "File uploaded", "filename": file.filename, "hash": file_hash})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
