from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chlorosis import analyze_image
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
FRONTEND_FOLDER = "../frontend"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Serve frontend
@app.route('/')
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

# Serve output images
@app.route('/outputs/<filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# Analyze route
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = analyze_image(filepath)

    if result is None:
        return jsonify({"error": "Leaf not detected"}), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)