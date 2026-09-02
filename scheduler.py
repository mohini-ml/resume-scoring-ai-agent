import schedule
import time
import os
from extract import extract_resume_text  # tumhara extract function
from score import score_resume                  # tumhara score function

# Yeh folder wo hai jaha "pending" resumes rakhoge scoring ke liye
PENDING_FOLDER = "pending_resumes"

def batch_score_job():
    print("[Scheduler] Batch scoring job started...")

    if not os.path.exists(PENDING_FOLDER):
        print("[Scheduler] No pending_resumes folder found. Skipping.")
        return

    files = os.listdir(PENDING_FOLDER)
    if not files:
        print("[Scheduler] No pending resumes found.")
        return

    for filename in files:
        filepath = os.path.join(PENDING_FOLDER, filename)
        print(f"[Scheduler] Scoring: {filename}")

        resume_text = extract_resume_text(filepath)

        result = score_resume(resume_text)

    print(f"[Scheduler] results for {filename}: {result}")


# Har din raat 12 baje chalega
schedule.every(10).seconds.do(batch_score_job)

print("Scheduler started. Waiting for scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(1)