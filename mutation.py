import copy
import numpy as np
from numpy.random import Generator, PCG64DXSM

from generation import Generation
from fitness_functions import evaluate_fitness
from Schedule_Generator import load_all_data

# --- RNG ---
# PCG64DXSM is higher quality than Python's default Mersenne Twister,
# especially important for large populations where MT can show correlations.
rng = Generator(PCG64DXSM())

# --- Constants ---
POPULATION_SIZE    = 1000
BASE_MUTATION_RATE = 0.01   # starting mutation rate
STOP_IMPROVEMENT   = 0.001  # near-zero floor — stop when improvement drops below this (Phase 2 only)
MAX_MUTATION_RATE  = 0.25   # cap: never mutate more than 25% of genes
MIN_MUTATION_RATE  = 0.001  # floor: never drop below 0.1%
MANDATORY_GENS     = 100    # minimum generations before stop condition is checked


def sort_schedules(schedules: list) -> list:
    """Sort schedules descending by fitness (higher = better)."""
    return sorted(schedules, key=lambda s: s.fitness, reverse=True)


def cull_bottom_half(schedules: list) -> list:
    """Keep only the top 50% of schedules."""
    sorted_schedules = sort_schedules(schedules)
    cutoff = len(sorted_schedules) // 2
    return sorted_schedules[:cutoff]


def softmax_select(schedules: list, n: int) -> list:
    """
    Select n schedules with probability proportional to softmax(fitness).
    Softmax converts raw fitness scores into a proper probability distribution,
    so fitter schedules are more likely to be chosen as parents without
    completely excluding weaker ones (preserving diversity).
    The subtraction of max(scores) before exp() is a standard numerical
    stability trick to prevent overflow.
    """
    scores = np.array([s.fitness for s in schedules], dtype=np.float64)
    scores -= scores.max()           # numerical stability
    weights = np.exp(scores)
    weights /= weights.sum()         # normalize to probabilities
    indices = rng.choice(len(schedules), size=n, replace=False, p=weights)
    return [schedules[i] for i in indices]


def crossover(parent_a, parent_b) -> tuple:
    """
    Single-point crossover: pick one splice index, everything before it
    comes from parent A, everything from it onward comes from parent B
    (and vice versa for the second child).
    Parents are deep-copied so originals are never modified.
    """
    num_genes = len(parent_a.genes)

    # randint(1, num_genes) ensures at least one gene from each parent
    idx = rng.integers(1, num_genes)

    child_a = copy.deepcopy(parent_a)
    child_b = copy.deepcopy(parent_b)

    child_a.genes = copy.deepcopy(parent_a.genes[:idx]) + copy.deepcopy(parent_b.genes[idx:])
    child_b.genes = copy.deepcopy(parent_b.genes[:idx]) + copy.deepcopy(parent_a.genes[idx:])

    child_a.fitness = 0.0
    child_b.fitness = 0.0

    return child_a, child_b


def mutate(schedule, mutation_rate: float, rooms: list, times: list, facilitators: list):
    """
    For each gene, independently roll against mutation_rate.
    If triggered, randomly replace the time, room, or facilitator.
    """
    for gene in schedule.genes:
        if rng.random() < mutation_rate:
            attribute = rng.choice(['time', 'room', 'facilitator'])
            if attribute == 'time':
                gene.time = rng.choice(times)
            elif attribute == 'room':
                gene.room = rng.choice(rooms)
            else:
                gene.facilitator = rng.choice(facilitators)


def score_population(schedules: list):
    """Evaluate and store fitness for every schedule in the list."""
    for schedule in schedules:
        evaluate_fitness(schedule)  # resets fitness to 0.0 and runs all checks internally


def run_one_generation(current_population, mutation_rate, rooms, times, facilitators):
    """
    Run a single generation cycle:
      1. Cull bottom 50%
      2. Softmax-weighted selection of parent pairs
      3. Single-point crossover to produce children
      4. Mutate children
      5. Score children
      6. Merge and re-sort, keeping top POPULATION_SIZE
    Returns the new population and its stats.
    """
    # --- Cull bottom 50% ---
    survivors = cull_bottom_half(current_population)

    # --- Softmax-weighted parent selection ---
    # Select the same number of parents as survivors so we produce enough children.
    # Pairing is done sequentially after selection (selected[0] x selected[1], etc.)
    n_parents = len(survivors) if len(survivors) % 2 == 0 else len(survivors) - 1
    selected = softmax_select(survivors, n_parents)

    children = []
    for i in range(0, n_parents, 2):
        child_a, child_b = crossover(selected[i], selected[i + 1])
        children.append(child_a)
        children.append(child_b)

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


def adapt_mutation_rate(mutation_rate: float, improvement: float) -> tuple[float, str]:
    """
    Adjust mutation rate based on rolling improvement.
    - Any positive improvement → halve rate (population is making progress, fine-tune)
    - Zero or negative improvement → double rate (population is stalling, explore)
    Returns the new rate and a log message (empty string if no change).
    """
    if improvement > 0:
        new_rate = max(mutation_rate / 2, MIN_MUTATION_RATE)
        direction = "down"
    else:
        new_rate = min(mutation_rate * 2, MAX_MUTATION_RATE)
        direction = "up"

    if new_rate != mutation_rate:
        msg = (f"  >> Rolling improvement ({improvement:.6f}) — "
               f"adjusting mutation rate {direction}: {mutation_rate:.6f} → {new_rate:.6f}")
    else:
        msg = ""
    return new_rate, msg


def compute_improvement(history: list, prev_avg: float, avg_fit: float) -> float:
    """
    Rolling average improvement per generation over the last 5 entries.
    Falls back to single-step delta when history is too short.
    """
    if len(history) >= 5:
        recent_avgs = [h['avg'] for h in history[-5:]]
        return (recent_avgs[-1] - recent_avgs[0]) / 4
    return avg_fit - prev_avg


def run_evolution():
    """
    Unified adaptive evolution loop.

    Every generation (including the mandatory first 100) uses the same
    adaptive mutation logic: rate doubles when progress stalls, halves
    when progress is strong. The only difference between Phase 1 and
    Phase 2 is that the stop condition is not checked until gen 100.
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
    gen_num = 1

    while True:
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

        improvement = compute_improvement(history, prev_avg, avg_fit)
        mutation_rate, rate_msg = adapt_mutation_rate(mutation_rate, improvement)
        if rate_msg:
            print(rate_msg)

        phase = "mandatory" if gen_num <= MANDATORY_GENS else "adaptive"
        print(f"Gen {gen_num:>3} [{phase}] — best: {best_fit:.3f}, avg: {avg_fit:.3f}, "
              f"worst: {worst_fit:.3f}, mutation: {mutation_rate:.6f}")

        if gen_num == MANDATORY_GENS:
            print("\n--- Mandatory 100 generations complete. Stop condition now active. ---\n")

        # stop condition only applies after mandatory phase
        if gen_num > MANDATORY_GENS and abs(improvement) < STOP_IMPROVEMENT:
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