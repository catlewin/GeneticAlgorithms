import matplotlib.pyplot as plt


# fitness stats printing

def print_fitness_stats(history: list[dict]):
    # print a table of fitness stats for each generation
    print(f"\n{'Gen':>4} {'Best':>8} {'Avg':>8} {'Worst':>8} {'Improv %':>10} {'Mut Rate':>10}")
    print("─" * 54)
    for i, record in enumerate(history):
        if i == 0:
            improvement = "—"
        else:
            prev_avg = history[i - 1]['avg']
            if prev_avg != 0:
                pct = ((record['avg'] - prev_avg) / abs(prev_avg)) * 100
                improvement = f"{pct:>9.2f}%"
            else:
                improvement = "—"
        print(f"{record['generation']:>4} {record['best']:>8.3f} {record['avg']:>8.3f} "
              f"{record['worst']:>8.3f} {improvement:>10} {record['mutation_rate']:>10.4f}")


# print the schedule

def print_schedule_by_time(schedule):
    # print the best schedule ordered by time slot
    TIME_ORDER = ["10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"]
    print(f"\n{'═' * 72}")
    print(f"  BEST SCHEDULE (ordered by time)     Fitness: {schedule.fitness:.3f}")
    print(f"{'═' * 72}")
    print(f"  {'TIME':<12} {'ACTIVITY':<12} {'ROOM':<18} {'FACILITATOR':<12}")
    print(f"{'─' * 72}")

    sorted_genes = sorted(
        schedule.genes,
        key=lambda g: TIME_ORDER.index(g.time) if g.time in TIME_ORDER else 99
    )
    for g in sorted_genes:
        room_str = f"{g.room.name} {g.room.room}"
        print(f"  {g.time:<12} {g.activity.name:<12} {room_str:<18} {g.facilitator:<12}")
    print(f"{'═' * 72}\n")


def print_schedule_by_activity(schedule):
    # print the best schedule ordered by activity (gene order)
    print(f"\n{'═' * 72}")
    print(f"  BEST SCHEDULE (ordered by activity)     Fitness: {schedule.fitness:.3f}")
    print(f"{'═' * 72}")
    print(f"  {'ACTIVITY':<12} {'TIME':<12} {'ROOM':<18} {'FACILITATOR':<12}")
    print(f"{'─' * 72}")

    for g in schedule.genes:
        room_str = f"{g.room.name} {g.room.room}"
        print(f"  {g.activity.name:<12} {g.time:<12} {room_str:<18} {g.facilitator:<12}")
    print(f"{'═' * 72}\n")


def print_schedule_by_building(schedule):
    # print the best schedule grouped by building
    print(f"\n{'═' * 72}")
    print(f"  BEST SCHEDULE (grouped by building)     Fitness: {schedule.fitness:.3f}")
    print(f"{'═' * 72}")

    buildings = {}
    for g in schedule.genes:
        bldg = g.room.name
        if bldg not in buildings:
            buildings[bldg] = []
        buildings[bldg].append(g)

    for bldg in sorted(buildings.keys()):
        print(f"\n  ┌─ {bldg} ─────────────────────────────────────────────")
        print(f"  │ {'ACTIVITY':<12} {'TIME':<12} {'ROOM':<18} {'FACILITATOR':<12}")
        print(f"  │{'─' * 58}")
        for g in buildings[bldg]:
            room_str = f"{g.room.name} {g.room.room}"
            print(f"  │ {g.activity.name:<12} {g.time:<12} {room_str:<18} {g.facilitator:<12}")
    print(f"\n{'═' * 72}\n")


def print_schedule_by_facilitator(schedule):
    # print the best schedule grouped by facilitator
    print(f"\n{'═' * 72}")
    print(f"  BEST SCHEDULE (grouped by facilitator)     Fitness: {schedule.fitness:.3f}")
    print(f"{'═' * 72}")

    fac_groups = {}
    for g in schedule.genes:
        if g.facilitator not in fac_groups:
            fac_groups[g.facilitator] = []
        fac_groups[g.facilitator].append(g)

    for fac in sorted(fac_groups.keys()):
        count = len(fac_groups[fac])
        print(f"\n  ┌─ {fac} ({count} activities) ──────────────────────────────")
        print(f"  │ {'ACTIVITY':<12} {'TIME':<12} {'ROOM':<18}")
        print(f"  │{'─' * 46}")
        for g in fac_groups[fac]:
            room_str = f"{g.room.name} {g.room.room}"
            print(f"  │ {g.activity.name:<12} {g.time:<12} {room_str:<18}")
    print(f"\n{'═' * 72}\n")


# fitness plot

def plot_fitness(history: list[dict], save_path: str = None):
    # plot best, average, and worst fitness over generations
    generations = [r['generation'] for r in history]
    best_scores = [r['best'] for r in history]
    avg_scores = [r['avg'] for r in history]
    worst_scores = [r['worst'] for r in history]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(generations, best_scores, label='Best', color='#2ecc71', linewidth=2)
    ax.plot(generations, avg_scores, label='Average', color='#3498db', linewidth=2)
    ax.plot(generations, worst_scores, label='Worst', color='#e74c3c', linewidth=2)

    ax.set_xlabel('Generation', fontsize=12)
    ax.set_ylabel('Fitness Score', fontsize=12)
    ax.set_title('Fitness Over Generations', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Plot saved to {save_path}")
    plt.show()


# entry point

if __name__ == "__main__":
    from mutation import run_evolution, sort_schedules

    final_population, history = run_evolution()

    # print fitness stats table
    print_fitness_stats(history)

    # print the best schedule in all formats
    best = sort_schedules(final_population)[0]
    print_schedule_by_time(best)
    print_schedule_by_activity(best)
    print_schedule_by_building(best)
    print_schedule_by_facilitator(best)

    # show the fitness plot
    plot_fitness(history, save_path="fitness_plot.png")
