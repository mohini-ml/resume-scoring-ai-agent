import shutil
import schedule
import time
import os
from extract import extract_resume_text
from score import score_resume
from parallel_score import process_resume
from queue_manager import get_remaining_quota, increment_usage, get_today_usage

PENDING_FOLDER = "pending_resumes"
PROCESSED_FOLDER = "processed"
FAILED_FOLDER = "failed"

os.makedirs(PENDING_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FAILED_FOLDER, exist_ok=True)



def batch_score_job():
    print("[Scheduler] Batch scoring job started...")

    if not os.path.exists(PENDING_FOLDER):
        print("[Scheduler] No pending_resumes folder found. Skipping.")
        return

    files = os.listdir(PENDING_FOLDER)
    if not files:
        print("[Scheduler] No pending resumes found.")
        return

    remaining = get_remaining_quota()
    used, limit = get_today_usage()
    print(f"[Scheduler] Today's usage: {used}/{limit}. Remaining quota: {remaining}")

    if remaining <= 0:
        print("[Scheduler] Daily quota exhausted. Resumes will stay queued for tomorrow.")
        return

    # Sirf utne hi files process karo jitni quota bachi hai
    files_to_process = files[:remaining]
    skipped = files[remaining:]

for filename in files_to_process:
    filename_res, result = process_resume(filename)
    print(f"[Scheduler] results for {filename_res}: {result}")
    increment_usage(1)

    src_path = os.path.join(PENDING_FOLDER, filename)
    if result.get("status") == "failed":
        dst_path = os.path.join(FAILED_FOLDER, filename)
    else:
        dst_path = os.path.join(PROCESSED_FOLDER, filename)

    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)

    if skipped:
        print(f"[Scheduler] {len(skipped)} resumes queued for tomorrow (quota reached): {skipped}")

if__name__ == "__main__":
    schedule.every(5).minutes.do(batch_score_job)

    print("Scheduler started. Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(1)