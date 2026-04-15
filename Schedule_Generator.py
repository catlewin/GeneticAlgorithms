import csv
import random
from schedule import Gene, Schedule
from activities import Activity
from rooms import Room
 
 
#  Load data from CSVs 
def load_courses(path="database/activities.csv") -> list[dict]:
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
                #current = Activity(class_name, int(enrollment), [preferred], [other])
                current = Activity(
                    name=class_name,
                    enrollment=int(enrollment),
                    preferred=[preferred] if preferred else [],
                    other=[other] if other else [],
                )
            elif current:  # continuation row — additional facilitators
                if preferred:
                    current.preferred.append(preferred)
                if other:
                    current.other.append(other)

    if current:
        courses.append(current)
    return courses
 
 
def load_rooms(path="rooms.csv") -> list[Room]:
    """Parse rooms.csv and return a list of Room objects."""
    rooms = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rooms.append(Room(
                name=row["Hall"].strip(),
                room=int(row["Room"].strip()),
                capacity=int(row["Capacity"].strip())
            ))
    return rooms
 
 
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
    courses: list[Activity],   # order is preserved — do not shuffle before passing
    rooms: list[Room],
    times: list[str],
    facilitators: list[str],
) -> Schedule:
    """Randomly assign a Room, time slot, and facilitator to each Activity.
    Genes are added in the same order as `courses`, which must be stable
    across all schedules so that index-based crossover works correctly."""
    schedule = Schedule()
    for activity in courses:
        gene = Gene(
            activity=activity,
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
        room_str = f"{g.room.name} {g.room.room}"  # e.g. "Beach 201"
        print(f"  {g.activity.name:<10} {g.time:<12} {room_str:<20} {g.facilitator}")
    print(f"{'─'*65}\n")

def print_in_activity_order(schedule: Schedule):
    print(f"  {'COURSE':<10} {'TIME':<12} {'ROOM':<16} FACILITATOR")
    print(f"{'─' * 65}")
    for g in schedule.genes:
        room_str = f"{g.room.name} {g.room.room}"  # e.g. "Beach 201"
        print(f"  {g.activity.name:<10} {g.time:<12} {room_str:<20} {g.facilitator}")
    print(f"{'─' * 65}\n")
 
#  Main 
 
if __name__ == "__main__":
    courses      = load_courses("database/activities.csv")
    rooms        = load_rooms("database/rooms.csv")
    times        = load_times("database/times.csv")
    facilitators = load_facilitators("database/facilitators.csv")
 
    print(f"Loaded {len(courses)} courses, {len(rooms)} rooms, "
          f"{len(times)} time slots, {len(facilitators)} facilitators.")

    schedule = generate_random_schedule(courses, rooms, times, facilitators)
    print_schedule(schedule)

    schedule2 = generate_random_schedule(courses, rooms, times, facilitators)
    print_schedule(schedule2)

    # print in activity order, to make sure consistent for all schedules
    # print_in_activity_order(schedule)
    # print_in_activity_order(schedule2)