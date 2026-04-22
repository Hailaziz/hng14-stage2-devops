import redis
import time
import os
import signal
import sys

running = True

def handle_signal(signum, frame):
    global running
    print("Shutdown signal received, finishing current job...")
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

if __name__ == "__main__":
    print("Worker started, waiting for jobs...")
    while running:
        job = r.brpop("jobs", timeout=5)
        if job:
            _, job_id = job
            process_job(job_id)
    print("Worker shut down cleanly.")
    sys.exit(0)
