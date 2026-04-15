import csv
import random
from schedule import Gene, Schedule
 
 
#  Load data from CSVs 
def load_courses(path="classes.csv") -> list[dict]:
    """Parse the multi-row classes.csv where preferred/other cols span several rows."""
    courses = []
    current = None
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            while len(row) < 4:
                row.append("")
            class_name = row[0].strip()
            enrollment = row[1].strip()
            preferred  = row[2].strip()
            other      = row[3].strip()
 
            if class_name:  # Start of a new course block
                if current:
                    courses.append(current)
                current = {
                    "name": class_name,
                    "expected_enrollment": int(enrollment),
                    "preferred": [preferred] if preferred else [],
                    "other": [other] if other else [],
                }
            elif current:   # Continuation row for the current course
                if preferred:
                    current["preferred"].append(preferred)
                if other:
                    current["other"].append(other)
 
    if current:
        courses.append(current)
    return courses
 
 
def load_rooms(path="rooms.csv") -> list[str]:
    """Returns room names as 'Hall Room' strings matching the fitness code format."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [f"{row['Hall']} {row['Room']}" for row in csv.DictReader(f)]
 
 
def load_times(path="times.csv") -> list[str]:
    """times.csv has no header — each line is a time string."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]
 
 
def load_facilitators(path="facilitators.csv") -> list[str]:
    """facilitators.csv has no header — each line is a name."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]
 
 
#  Schedule generation 
 
def generate_random_schedule(
    courses: list[dict],
    rooms: list[str],
    times: list[str],
    facilitators: list[str],
) -> Schedule:
    """Randomly assign a room, time, and facilitator to each course.
    Returns a Schedule of Gene objects compatible with the fitness functions."""
    schedule = Schedule()
    for course in courses:
        gene = Gene(
            activity=course["name"],
            time=random.choice(times),
            room=random.choice(rooms),
            facilitator=random.choice(facilitators),
        )
        schedule.add_gene(gene)
    return schedule
 
 
#  Display 
 
def print_schedule(schedule: Schedule):
    TIME_ORDER = ["10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"]
    print(f"\n{'─'*65}")
    print(f"  {'COURSE':<10} {'TIME':<12} {'ROOM':<16} FACILITATOR")
    print(f"{'─'*65}")
    for g in sorted(schedule.genes, key=lambda x: TIME_ORDER.index(x.time) if x.time in TIME_ORDER else 99):
        print(f"  {g.activity:<10} {g.time:<12} {g.room:<16} {g.facilitator}")
    print(f"{'─'*65}\n")
 
 
#  Main 
 
if __name__ == "__main__":
    courses      = load_courses("classes.csv")
    rooms        = load_rooms("rooms.csv")
    times        = load_times("times.csv")
    facilitators = load_facilitators("facilitators.csv")
 
    print(f"Loaded {len(courses)} courses, {len(rooms)} rooms, "
          f"{len(times)} time slots, {len(facilitators)} facilitators.")
 
    schedule = generate_random_schedule(courses, rooms, times, facilitators)
    print_schedule(schedule)