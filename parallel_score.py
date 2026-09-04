import os
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from extract import extract_resume_text
from score import score_resume

PENDING_FOLDER = "pending_resumes"

def process_resume(filename, max_retries=3):
    filepath = os.path.join(PENDING_FOLDER, filename)
    print(f"[Parallel] Processing: {filename}")

    resume_text = extract_resume_text(filepath)

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = score_resume(resume_text)
            return filename, result
        except Exception as e:
            last_error = e
            error_str = str(e)

            if "429" in error_str or "TooManyRequests" in error_str or "quota" in error_str.lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"[Parallel] Rate limit hit for {filename}. Retry {attempt}/{max_retries} in {wait_time:.1f}s...")
            else:
                wait_time = 2 * attempt
                print(f"[Parallel] Error for {filename}: {error_str[:100]}. Retry {attempt}/{max_retries} in {wait_time}s...")

            time.sleep(wait_time)

    print(f"[Parallel] FAILED after {max_retries} attempts: {filename}")
    return filename, {"error": str(last_error), "status": "failed"}
def run_parallel_scoring():
    if not os.path.exists(PENDING_FOLDER):
        print("[Parallel] No pending_resumes folder found.")
        return

    files = os.listdir(PENDING_FOLDER)
    if not files:
        print("[Parallel] No pending resumes found.")
        return

    print(f"[Parallel] Starting parallel scoring for {len(files)} resumes...")

    all_results = {}
    completed_count = 0
    total = len(files)

    # max_workers = kitne resumes ek saath process honge
    with ThreadPoolExecutor(max_workers=3) as executor:
         futures = {executor.submit(process_resume, f): f for f in files}

    for future in as_completed(futures):
            filename, result = future.result()
            all_results[filename] = result
            completed_count += 1
            print(f"[Parallel] ({completed_count}/{total}) Done: {filename}")

    # Save all results to a JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"[Parallel] All resumes processed. Results saved to {output_file}")

if __name__ == "__main__":
    run_parallel_scoring()