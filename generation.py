from schedule import Schedule, Gene
from Schedule_Generator import generate_random_schedule, load_all_data


class Generation:
    def __init__(self):
        self.schedules = []
        self.best_fit = None
        self.avg_fit = None
        self.worst_fit = None
        self.gen_improvement = None
    def generate_gen0(self):
        courses, rooms, times, facilitators = load_all_data()
        for i in range(1000):
            schedule = generate_random_schedule(courses, rooms, times, facilitators)
            self.schedules.append(schedule)
            if i == 0:
                print(schedule.genes[0].time, schedule.genes[1].time)

if __name__ == "__main__":
    my_generation = Generation()
    my_generation.generate_gen0()
    print(len(my_generation.schedules))
    print(my_generation.schedules[0].genes[0].time)