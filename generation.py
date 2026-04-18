from schedule import Schedule, Gene
from Schedule_Generator import generate_random_schedule, load_all_data
from fitness_functions import evaluate_fitness


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
    def calc_fitness(self):
        fitness_scores = []
        best = None
        worst = None
        for i in range(1000):
            evaluate_fitness(self.schedules[i])
            fitness_scores.append(self.schedules[i].fitness)
            if best is None or self.schedules[i].fitness > best.fitness:
                best = self.schedules[i]
            if worst is None or self.schedules[i].fitness < worst.fitness:
                worst = self.schedules[i]
        self.best_fit = best.fitness
        self.worst_fit = worst.fitness
        self.avg_fit = sum(fitness_scores) / len(fitness_scores)

if __name__ == "__main__":
    my_generation = Generation()
    my_generation.generate_gen0()
    my_generation.calc_fitness()
    print(len(my_generation.schedules))
    print(my_generation.schedules[0].genes[0].time)
    print(my_generation.schedules[0].fitness)
    print(my_generation.schedules[1].fitness)
    print(my_generation.schedules[2].fitness)

    print(my_generation.best_fit)
    print(my_generation.worst_fit)
    print(my_generation.avg_fit)
