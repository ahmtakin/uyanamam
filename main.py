import time
from datetime import datetime
from enroll import enroll

# 📌 Set your target enrollment time
ENROLLMENT_TIME = "16:27:00"  # Format: HH:MM:SS

# 📌 CRNs you want to enroll in
CRNS = ["21974"]

# 📌 How many times to retry
MAX_ATTEMPTS = 10  # Set to None for infinite


def wait_until(target_time_str: str):
    """Waits until the given HH:MM:SS time today."""
    now = datetime.now()
    target_time = datetime.strptime(target_time_str, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )

    print(f"[i] Waiting until {target_time.strftime('%H:%M:%S')} to begin enrollment...")

    while datetime.now() < target_time:
        time.sleep(0.4)

    print("[✓] Target time reached. Starting repeated enrollment...")


def repeatedly_enroll(crns, interval=2, max_attempts=MAX_ATTEMPTS):
    """Calls enroll every `interval` seconds, up to `max_attempts` times."""
    attempt = 0
    while max_attempts is None or attempt < max_attempts:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempt {attempt + 1}")
        enroll(crns)
        attempt += 1
        time.sleep(interval)


if __name__ == "__main__":
    wait_until(ENROLLMENT_TIME)
    repeatedly_enroll(CRNS)
