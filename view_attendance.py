"""
view_attendance.py
--------------------
Quick script to print today's attendance log to the console.
Run this anytime to check who's been marked present today.
"""

from database import init_db, get_today_attendance


def view_attendance():
    init_db()
    records = get_today_attendance()

    if not records:
        print("No attendance recorded yet today.")
        return

    print("\n--- Today's Attendance ---")
    print(f"{'Name':<20} {'Time':<20}")
    print("-" * 40)
    for row in records:
        # timestamp is stored as ISO format, just show the time portion cleanly
        time_only = row["timestamp"].split("T")[1].split(".")[0]
        print(f"{row['name']:<20} {time_only:<20}")


if __name__ == "__main__":
    view_attendance()
