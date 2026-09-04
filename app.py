import os
from flask import Flask, request, jsonify
from extract import extract_resume_text
from score import score_resume_with_jd

app = Flask(__name__)

# Uploads folder setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/score", methods=["POST"])
def score_endpoint():
    # 1. Check if file is provided in request
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Use form-data key 'file'."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    # 2. Get optional Job Description from form parameters
    job_description = request.form.get("job_description", "General AI / Software Engineer")

    # 3. Save file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Extract text & calculate score with ATS JD matching
        resume_text = extract_resume_text(file_path)
        result = score_resume_with_jd(resume_text, job_description)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # 4. Clean up uploaded file (Data privacy / Minimal storage principle)
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Resume Scoring & ATS Agent API is running.",
        "usage": "POST a resume file to /score with optional 'job_description' field."
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)