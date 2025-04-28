from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import uuid
from music_gen import generate_music_from_image

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-music', methods=['POST'])
def generate_music_route():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    image = request.files['image']
    filename = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join("static/uploads", filename)
    image.save(image_path)

    output_audio_path = generate_music_from_image(image_path)

    if not os.path.exists(output_audio_path):
        return jsonify({"success": False, "error": "Music generation failed"}), 500

    audio_url = "/" + output_audio_path.replace("\\", "/")
    return jsonify({"success": True, "audio_url": audio_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
