import requests

url = "http://127.0.0.1:5000/score"
file_path = "sample_resume.docx.docx"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())