import requests

url = "http://127.0.0.1:5000/score"
file_path = "sample_resume.docx.docx" # Aapke folder me jo resume file hai

# Send file along with Job Description
data = {
    "job_description": "Looking for a Python Developer with experience in AI, Machine Learning, and REST APIs."
}

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files, data=data)

    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(response.json())

except Exception as e:
    print("Error testing API:", e)