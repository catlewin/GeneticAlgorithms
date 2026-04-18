import random
import copy
from generation import Generation
from fitness_functions import evaluate_fitness
from cs_activity_specific_adjustments import activity_specific_score
from Schedule_Generator import load_all_data
 
 
# --- Constants ---
POPULATION_SIZE = 1000
BASE_MUTATION_RATE = 0.01        # 1% per gene normally
PLATEAU_MUTATION_RATE = 0.05     # 5% per gene when fitness has plateaued
PLATEAU_THRESHOLD = 0.01         # avg fitness must improve by this much to not count as plateau
PLATEAU_WINDOW = 5               # number of generations of no improvement before escalating mutation
 
 
def sort_schedules(schedules: list) -> list:
    """Sort schedules descending by fitness (higher = better)."""
    return sorted(schedules, key=lambda s: s.fitness, reverse=True)
 
 
def death_to_bottom_half(schedules: list) -> list:
    """Keep only the top 50% of schedules."""
    sorted_schedules = sort_schedules(schedules)
    cutoff = len(sorted_schedules) // 2
    return sorted_schedules[:cutoff]
 
 
def crossover(parent_a, parent_b) -> tuple:
    """
    Produce two children by swapping a random gene slice between two parents.
    Each pair gets its own independently random splice range.
    Parents are copied so originals are not mutated.
    """
    num_genes = len(parent_a.genes)
 
    # pick two distinct indices for the splice range
    idx1, idx2 = sorted(random.sample(range(num_genes), 2))
 
    child_a = copy.deepcopy(parent_a)
    child_b = copy.deepcopy(parent_b)
 
    # swap the slice between the two children
    child_a.genes[idx1:idx2] = copy.deepcopy(parent_b.genes[idx1:idx2])
    child_b.genes[idx1:idx2] = copy.deepcopy(parent_a.genes[idx1:idx2])
 
    child_a.fitness = 0.0
    child_b.fitness = 0.0
 
    return child_a, child_b
 
 
def mutate(schedule, mutation_rate: float, rooms: list, times: list, facilitators: list):
    """
    For each gene, independently roll against mutation_rate.
    If triggered, randomly replace the time, room, or facilitator.
    """
    for gene in schedule.genes:
        if random.random() < mutation_rate:
            attribute = random.choice(['time', 'room', 'facilitator'])
            if attribute == 'time':
                gene.time = random.choice(times)
            elif attribute == 'room':
                gene.room = random.choice(rooms)
            else:
                gene.facilitator = random.choice(facilitators)
 
 
def score_population(schedules: list):
    """Evaluate and store fitness for every schedule in the list."""
    for schedule in schedules:
        schedule.fitness = activity_specific_score(schedule)
        evaluate_fitness(schedule)
 
 
def get_mutation_rate(avg_history: list) -> float:
    """
    Return an elevated mutation rate if avg fitness has plateaued
    over the last PLATEAU_WINDOW generations, otherwise return base rate.
    """
    if len(avg_history) < PLATEAU_WINDOW:
        return BASE_MUTATION_RATE
 
    recent = avg_history[-PLATEAU_WINDOW:]
    improvement = recent[-1] - recent[0]
    if improvement < PLATEAU_THRESHOLD:
        return PLATEAU_MUTATION_RATE
 
    return BASE_MUTATION_RATE
 
 
def run_evolution(num_generations: int = 100):
    """
    Main loop:
      1. Generate generation 0
      2. For each subsequent generation:
         a. Kill bottom 50%
         b. Crossover survivors to refill population
         c. Mutate (rate scales up on plateau)
         d. Score new population
         e. Merge and re-sort
         f. Record stats
    """
    _, rooms, times, facilitators = load_all_data()
 
    # --- Generation 0 ---
    print("Generating generation 0...")
    gen0 = Generation()
    gen0.generate_gen0()
    gen0.calc_fitness()
 
    history = []  # list of dicts, one per generation
 
    history.append({
        'generation': 0,
        'best': gen0.best_fit,
        'worst': gen0.worst_fit,
        'avg': gen0.avg_fit,
        'mutation_rate': BASE_MUTATION_RATE,
    })
 
    print(f"Gen 0 — best: {gen0.best_fit:.3f}, avg: {gen0.avg_fit:.3f}, worst: {gen0.worst_fit:.3f}")
 
    current_population = gen0.schedules
 
    avg_history = [gen0.avg_fit]
 
    for gen_num in range(1, num_generations + 1):
 
        # --- Kill bottom 50% ---
        survivors = death_to_bottom_half(current_population)   # 500 schedules
 
        # --- Crossover: randomly pair survivors to produce 500 new children ---
        shuffled = survivors[:]
        random.shuffle(shuffled)
 
        children = []
        for i in range(0, len(shuffled) - 1, 2):
            child_a, child_b = crossover(shuffled[i], shuffled[i + 1])
            children.append(child_a)
            children.append(child_b)
 
        # if odd number of survivors, carry last one over unchanged
        if len(shuffled) % 2 == 1:
            children.append(copy.deepcopy(shuffled[-1]))
 
        # --- Mutation ---
        mutation_rate = get_mutation_rate(avg_history)
        for child in children:
            mutate(child, mutation_rate, rooms, times, facilitators)
 
        # --- Score the new children ---
        score_population(children)
 
        # --- Merge survivors + children, then re-sort ---
        merged = survivors + children
        merged = sort_schedules(merged)
 
        # keep population fixed at POPULATION_SIZE
        current_population = merged[:POPULATION_SIZE]
 
        # --- Collect stats ---
        fitness_scores = [s.fitness for s in current_population]
        best_fit  = fitness_scores[0]   # sorted descending
        worst_fit = fitness_scores[-1]
        avg_fit   = sum(fitness_scores) / len(fitness_scores)
 
        avg_history.append(avg_fit)
 
        history.append({
            'generation': gen_num,
            'best': best_fit,
            'worst': worst_fit,
            'avg': avg_fit,
            'mutation_rate': mutation_rate,
        })
 
        print(f"Gen {gen_num:>3} — best: {best_fit:.3f}, avg: {avg_fit:.3f}, "
              f"worst: {worst_fit:.3f}, mutation: {mutation_rate}")
 
    print("\n--- Evolution complete ---")
    print(f"Final best fitness: {history[-1]['best']:.3f}")
 
    return current_population, history
 
 
if __name__ == "__main__":
    final_population, history = run_evolution(num_generations=100)
 
    print("\n--- Generation History Summary ---")
    print(f"{'Gen':>4} {'Best':>8} {'Avg':>8} {'Worst':>8} {'Mut Rate':>10}")
    print("-" * 44)
    for record in history:
        print(f"{record['generation']:>4} {record['best']:>8.3f} {record['avg']:>8.3f} "
              f"{record['worst']:>8.3f} {record['mutation_rate']:>10.4f}")