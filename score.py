"""
GENERALIZATION NOTE:
Yeh scoring agent sirf resumes tak limited nahi hai.
Isi function ka structure kisi bhi text-based document
(jaise: product description, cover letter, business proposal,
job posting, essay, etc.) ko score karne ke liye reuse kiya
ja sakta hai — bas prompt (upar wala instruction jo Gemini ko
bhejte hain) change karna hoga according to use-case.

Example: agar "resume" ko "product description" se replace
karke prompt mein criteria badal do (jaise clarity, USP,
target audience), toh yehi agent product descriptions bhi
score kar dega. Core logic (extract -> score -> structured
JSON output) same rahega.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport="rest")
model = genai.GenerativeModel("gemini-3.8-flash")
import time
from google.api_core.exceptions import ResourceExhausted

def call_gemini_with_retry(model, prompt, max_retries=5, base_delay=5, **kwargs):
    """Calls Gemini API with automatic retry on rate-limit (429) errors."""
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt, **kwargs)
            return response
        except ResourceExhausted as e:
            wait_time = base_delay * attempt
            print(f"⚠️ Rate limit hit (attempt {attempt}/{max_retries}). Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    raise Exception("Max retries exceeded. Gemini API is still rate-limited.")
def score_resume(resume_text):
    prompt = f"""
You are an expert recruiter and resume evaluator.

Analyze the following resume text and score it from 0 to 100 based on:
- Clarity and structure
- Relevant skills and experience
- Achievements and impact
- Overall job-readiness

Resume Text:
\"\"\"{resume_text}\"\"\"

Respond ONLY in valid JSON format, with no extra text, no markdown, no explanation outside JSON.
Use exactly this structure:
{{
  "score": <integer 0-100>,
  "strengths": ["point1", "point2", "..."],
  "weaknesses": ["point1", "point2", "..."],
  "suggestions": ["point1", "point2", "..."]
}}
"""

    response = call_gemini_with_retry(model, prompt,request_options={"timeout": 60})
                                        
    raw_text = response.text.strip()

    # Clean up in case Gemini wraps it in ```json ... ```
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "error": "Failed to parse JSON from Gemini response",
            "raw_response": raw_text
        }

    return result


if __name__ == "__main__":
    from extract import extract_resume_text

    resume_text = extract_resume_text("sample_resume.docx.docx")
    result = score_resume(resume_text)

    print(json.dumps(result, indent=2))