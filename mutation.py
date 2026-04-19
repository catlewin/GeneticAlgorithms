import random
import copy
from generation import Generation
from fitness_functions import evaluate_fitness
from cs_activity_specific_adjustments import activity_specific_score
from Schedule_Generator import load_all_data


# --- Constants ---
POPULATION_SIZE   = 1000
BASE_MUTATION_RATE = 0.01   # 1% per gene to start
MIN_IMPROVEMENT   = 0.01    # 1% threshold — if avg fitness improves less than this, halve mutation rate
STOP_IMPROVEMENT  = 0.001   # near-zero floor — stop when improvement drops below this


def sort_schedules(schedules: list) -> list:
    """Sort schedules descending by fitness (higher = better)."""
    return sorted(schedules, key=lambda s: s.fitness, reverse=True)


def cull_bottom_half(schedules: list) -> list:
    """Keep only the top 50% of schedules."""
    sorted_schedules = sort_schedules(schedules)
    cutoff = len(sorted_schedules) // 2
    return sorted_schedules[:cutoff]


def crossover(parent_a, parent_b) -> tuple:
    """
    Produce two children by swapping a random gene slice between two parents.
    Each pair gets its own independently random splice range.
    Parents are deep-copied so originals are not mutated.
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


def run_one_generation(current_population, mutation_rate, rooms, times, facilitators):
    """
    Run a single generation cycle:
      1. Cull bottom 50%
      2. Crossover survivors into new children
      3. Mutate children
      4. Score children
      5. Merge and re-sort, keeping top POPULATION_SIZE
    Returns the new population and its stats.
    """
    # --- Cull bottom 50% ---
    survivors = cull_bottom_half(current_population)

    # --- Crossover: randomly pair survivors to produce children ---
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

    # --- Mutate children ---
    for child in children:
        mutate(child, mutation_rate, rooms, times, facilitators)

    # --- Score children ---
    score_population(children)

    # --- Merge, re-sort, trim ---
    merged = sort_schedules(survivors + children)
    new_population = merged[:POPULATION_SIZE]

    # --- Stats ---
    fitness_scores = [s.fitness for s in new_population]
    best_fit  = fitness_scores[0]
    worst_fit = fitness_scores[-1]
    avg_fit   = sum(fitness_scores) / len(fitness_scores)

    return new_population, best_fit, avg_fit, worst_fit


def run_evolution():
    """
    Main loop:

    Phase 1 — first 100 generations (mandatory):
      Run unconditionally, using BASE_MUTATION_RATE.

    Phase 2 — after 100 generations:
      Each generation, compute improvement = current_avg - previous_avg.
      - If improvement < MIN_IMPROVEMENT (1%): halve the mutation rate and keep going.
      - If improvement < STOP_IMPROVEMENT (near zero): stop.
    """
    _, rooms, times, facilitators = load_all_data()

    # --- Generation 0 ---
    print("Generating generation 0...")
    gen0 = Generation()
    gen0.generate_gen0()
    gen0.calc_fitness()

    history = [{
        'generation': 0,
        'best': gen0.best_fit,
        'worst': gen0.worst_fit,
        'avg': gen0.avg_fit,
        'mutation_rate': BASE_MUTATION_RATE,
    }]

    print(f"Gen   0 — best: {gen0.best_fit:.3f}, avg: {gen0.avg_fit:.3f}, "
          f"worst: {gen0.worst_fit:.3f}, mutation: {BASE_MUTATION_RATE:.6f}")

    current_population = gen0.schedules
    prev_avg = gen0.avg_fit
    mutation_rate = BASE_MUTATION_RATE

    # ---- Phase 1: mandatory 100 generations ----
    for gen_num in range(1, 101):
        current_population, best_fit, avg_fit, worst_fit = run_one_generation(
            current_population, mutation_rate, rooms, times, facilitators
        )

        history.append({
            'generation': gen_num,
            'best': best_fit,
            'worst': worst_fit,
            'avg': avg_fit,
            'mutation_rate': mutation_rate,
        })

        print(f"Gen {gen_num:>3} — best: {best_fit:.3f}, avg: {avg_fit:.3f}, "
              f"worst: {worst_fit:.3f}, mutation: {mutation_rate:.6f}")

        prev_avg = avg_fit

    print("\n--- Mandatory 100 generations complete. Entering adaptive phase. ---\n")

    # ---- Phase 2: adaptive stopping ----
    gen_num = 101
    while True:
        current_population, best_fit, avg_fit, worst_fit = run_one_generation(
            current_population, mutation_rate, rooms, times, facilitators
        )

        # append first so the rolling window includes the current generation
        history.append({
            'generation': gen_num,
            'best': best_fit,
            'worst': worst_fit,
            'avg': avg_fit,
            'mutation_rate': mutation_rate,
        })

        # rolling window: average improvement per generation over last 5 gens
        if len(history) >= 5:
            recent_avgs = [h['avg'] for h in history[-5:]]
            improvement = (recent_avgs[-1] - recent_avgs[0]) / 4
        else:
            improvement = avg_fit - prev_avg

        # halve condition: avg improvement dropped below 1%
        if improvement < MIN_IMPROVEMENT:
            mutation_rate /= 2
            print(f"  >> Rolling improvement ({improvement:.6f}) < {MIN_IMPROVEMENT} — "
                  f"halving mutation rate to {mutation_rate:.6f}")

        print(f"Gen {gen_num:>3} — best: {best_fit:.3f}, avg: {avg_fit:.3f}, "
              f"worst: {worst_fit:.3f}, mutation: {mutation_rate:.6f}")

        # stop condition: rolling improvement is near zero even after halving
        if abs(improvement) < STOP_IMPROVEMENT:
            print(f"\nStopping: rolling improvement ({improvement:.6f}) is below floor ({STOP_IMPROVEMENT}).")
            break

        prev_avg = avg_fit
        gen_num += 1

    print("\n--- Evolution complete ---")
    print(f"Total generations: {gen_num}")
    print(f"Final best fitness: {history[-1]['best']:.3f}")
    print(f"Final avg fitness:  {history[-1]['avg']:.3f}")
    print(f"Final mutation rate: {history[-1]['mutation_rate']:.6f}")

    return current_population, history


if __name__ == "__main__":
    final_population, history = run_evolution()

    print("\n--- Generation History Summary ---")
    print(f"{'Gen':>4} {'Best':>8} {'Avg':>8} {'Worst':>8} {'Mut Rate':>10}")
    print("-" * 44)
    for record in history:
        print(f"{record['generation']:>4} {record['best']:>8.3f} {record['avg']:>8.3f} "
              f"{record['worst']:>8.3f} {record['mutation_rate']:>10.6f}")