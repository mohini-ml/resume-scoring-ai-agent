import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from extract import extract_resume_text
from score import score_resume

PENDING_FOLDER = "pending_resumes"

def process_resume(filename):
    filepath = os.path.join(PENDING_FOLDER, filename)
    print(f"[Parallel] Processing: {filename}")

    resume_text = extract_resume_text(filepath)
    result = score_resume(resume_text)

    return filename, result

def run_parallel_scoring():
    if not os.path.exists(PENDING_FOLDER):
        print("[Parallel] No pending_resumes folder found.")
        return

    files = os.listdir(PENDING_FOLDER)
    if not files:
        print("[Parallel] No pending resumes found.")
        return

    print(f"[Parallel] Starting parallel scoring for {len(files)} resumes...")

    # max_workers = kitne resumes ek saath process honge
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_resume, f): f for f in files}

        for future in as_completed(futures):
            filename, result = future.result()
            print(f"[Parallel] Result for {filename}: {result}")

    print("[Parallel] All resumes processed.")

if __name__ == "__main__":
    run_parallel_scoring()