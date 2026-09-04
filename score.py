import json
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"), transport="rest")

# Model configuration
model = genai.GenerativeModel("gemini-1.5-flash")


def call_gemini_with_retry(model, prompt, max_retries=5, base_delay=5, **kwargs):
    """
    Calls Gemini API with exponential backoff on rate-limit (429) errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt, **kwargs)
            return response
        except ResourceExhausted:
            wait_time = base_delay * attempt
            print(f"⚠️ Rate limit hit (attempt {attempt}/{max_retries}). Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    raise Exception("Max retries exceeded. Gemini API rate-limited.")

def score_resume_with_jd(resume_text, job_description="General AI / Software Engineer", max_loops=3):
    # Model instance standard name ke sath
    model_instance = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = f"""
You are an expert ATS (Applicant Tracking System) recruiter and resume evaluator.

Compare the following Resume against the Job Description.

Job Description:
"{job_description}"

Resume Text:
"{resume_text}"

Respond ONLY in valid JSON format with no extra text, no markdown.
Use exactly this structure:
{{
  "match_score": 85,
  "ats_compatibility": "High",
  "matching_skills": ["Python", "Machine Learning"],
  "missing_skills": ["Docker", "Kubernetes"],
  "strengths": ["Strong background in AI", "Clear achievements"],
  "weaknesses": ["Missing portfolio links"],
  "recommendations": ["Add GitHub profile link", "Highlight deployment experience"]
}}
"""
    current_prompt = prompt

    for loop_count in range(1, max_loops + 1):
        try:
            # Direct API call with error handling
            response = call_gemini_with_retry(model_instance, current_prompt)
            raw_text = response.text.strip()

            if "```" in raw_text:
                parts = raw_text.split("```")
                raw_text = parts[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            result = json.loads(raw_text)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ [Loop Guard] Parsing failed on attempt {loop_count}/{max_loops}. Self-correcting...")
            current_prompt += f"\n\nERROR: Your response was not valid JSON ({str(e)}). Return strictly valid JSON ONLY."
        except Exception as e:
            # Fallback to gemini-pro if gemini-1.5-flash gives 404 on older library version
            if "404" in str(e):
                print("⚠️ Retrying with gemini-pro model...")
                model_instance = genai.GenerativeModel('models/gemini-pro')
                continue
            raise e

    return {
        "status": "failed",
        "error": "Loop Guard Triggered: Could not parse JSON from Gemini after retries."
    }

if __name__ == "__main__":
    from extract import extract_resume_text
    
    # Quick Test
    sample_path = "sample_resume.docx.docx"
    if os.path.exists(sample_path):
        text = extract_resume_text(sample_path)
        output = score_resume_with_jd(text, "Python AI Developer")
        print(json.dumps(output, indent=2))