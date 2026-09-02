from flask import Flask, request, jsonify
import os
from extract import extract_resume_text
from score import score_resume

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/score", methods=["POST"])
def score_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Use form-data key 'file'."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        resume_text = extract_resume_text(file_path)
        result = score_resume(resume_text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file (minimal data storage principle)
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(result)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Resume Scoring Agent API is running. POST a resume file to /score"})


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)