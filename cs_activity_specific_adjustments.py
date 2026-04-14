# time string to numeric hour mapping

TIME_TO_HOUR = {
    "10:00 AM": 10,
    "11:00 AM": 11,
    "12:00 PM": 12,
    "1:00 PM": 13,
    "2:00 PM": 14,
    "3:00 PM": 15,
}

# helper to check if a room is in the Roman or Beach building
def is_roman_or_beach(room_name: str) -> bool:
    # return True if the room belongs to Roman or Beach hall
    return room_name.startswith("Roman") or room_name.startswith("Beach")


# helper to compute the absolute hour gap between two time strings
def hour_gap(time_a: str, time_b: str) -> int:
    # return the absolute difference in hours between two time slots
    return abs(TIME_TO_HOUR[time_a] - TIME_TO_HOUR[time_b])


# helper to find a gene by activity name
def find_gene(genes, activity_name: str):
    # find and return the Gene with the matching activity name
    for gene in genes:
        if gene.activity == activity_name:
            return gene
    return None


# the main function
def activity_specific_score(schedule) -> float:
    genes = schedule.genes
    score = 0.0

    # find the four relevant genes by activity name
    gene_101a = find_gene(genes, "101 A")
    gene_101b = find_gene(genes, "101 B")
    gene_191a = find_gene(genes, "191 A")
    gene_191b = find_gene(genes, "191 B")

    # safety check, if any are missing then can't score these rules
    if not all([gene_101a, gene_101b, gene_191a, gene_191b]):
        return 0.0

    # rule 1: SLA 101 section A vs section B
    gap_101 = hour_gap(gene_101a.time, gene_101b.time)

    if gap_101 > 4:
        score += 0.5       # sections are far apart -> reward
    elif gap_101 == 0:
        score -= 0.5       # same time slot -> penalty

    # rule 2: SLA 191 section A vs section B
    gap_191 = hour_gap(gene_191a.time, gene_191b.time)

    if gap_191 > 4:
        score += 0.5       # sections are far apart -> reward
    elif gap_191 == 0:
        score -= 0.5       # same time slot -> penalty

    # rule 3: Every SLA 101 section <-> every SLA 191 section
    # Four pairs: (101A,191A), (101A,191B), (101B,191A), (101B,191B)

    cross_pairs = [
        (gene_101a, gene_191a),
        (gene_101a, gene_191b),
        (gene_101b, gene_191a),
        (gene_101b, gene_191b),
    ]

    for gene_x, gene_y in cross_pairs:
        gap = hour_gap(gene_x.time, gene_y.time)

        if gap == 1:
            # consecutive time slots -> reward
            score += 0.5

            # building-separation penalty
            x_in_rb = is_roman_or_beach(gene_x.room)
            y_in_rb = is_roman_or_beach(gene_y.room)
            if x_in_rb != y_in_rb:
                score -= 0.4

        elif gap == 2:
            # separated by exactly 1 hour gap -> small reward
            score += 0.25

        elif gap == 0:
            # same time slot -> penalty
            score -= 0.25

    return score


# test

if __name__ == "__main__":
    from schedule import Gene, Schedule

    # build a test schedule
    test_schedule = Schedule()
    test_schedule.add_gene(Gene("101 A", "10:00 AM", "Roman 201", "Glen"))
    test_schedule.add_gene(Gene("101 B", "3:00 PM",  "Beach 201", "Lock"))
    test_schedule.add_gene(Gene("191 A", "11:00 AM", "Frank 119", "Banks"))
    test_schedule.add_gene(Gene("191 B", "2:00 PM",  "Loft 206",  "Shaw"))
    test_schedule.add_gene(Gene("201",   "12:00 PM", "James 325", "Singer"))
    test_schedule.add_gene(Gene("291",   "1:00 PM",  "Loft 310",  "Uther"))
    test_schedule.add_gene(Gene("303",   "10:00 AM", "Beach 301", "Zeldin"))
    test_schedule.add_gene(Gene("304",   "11:00 AM", "Roman 216", "Tyler"))
    test_schedule.add_gene(Gene("394",   "12:00 PM", "Slater 003","Richards"))
    test_schedule.add_gene(Gene("449",   "1:00 PM",  "Beach 201", "Numen"))
    test_schedule.add_gene(Gene("451",   "2:00 PM",  "Frank 119", "Lock"))

    result = activity_specific_score(test_schedule)

    print("=== Activity-Specific Adjustment — Sanity Test ===\n")

    gap_101 = hour_gap("10:00 AM", "3:00 PM")
    print(f"SLA101 A vs B gap: {gap_101} hours → {'> 4 → +0.5' if gap_101 > 4 else 'no bonus'}")

    gap_191 = hour_gap("11:00 AM", "2:00 PM")
    print(f"SLA191 A vs B gap: {gap_191} hours → {'> 4 → +0.5' if gap_191 > 4 else 'no section bonus'}")

    pairs_desc = [
        ("101A(10AM,Roman201)", "191A(11AM,Frank119)", "10:00 AM", "11:00 AM", "Roman 201", "Frank 119"),
        ("101A(10AM,Roman201)", "191B(2PM,Loft206)",   "10:00 AM", "2:00 PM",  "Roman 201", "Loft 206"),
        ("101B(3PM,Beach201)",  "191A(11AM,Frank119)", "3:00 PM",  "11:00 AM", "Beach 201", "Frank 119"),
        ("101B(3PM,Beach201)",  "191B(2PM,Loft206)",   "3:00 PM",  "2:00 PM",  "Beach 201", "Loft 206"),
    ]

    print("\nCross-pair analysis:")
    for desc_x, desc_y, tx, ty, rx, ry in pairs_desc:
        g = hour_gap(tx, ty)
        rb_x = is_roman_or_beach(rx)
        rb_y = is_roman_or_beach(ry)
        detail = f"gap={g}h"
        if g == 1:
            detail += " → consecutive +0.5"
            if rb_x != rb_y:
                detail += ", building split -0.4"
        elif g == 2:
            detail += " → 1hr gap +0.25"
        elif g == 0:
            detail += " → same slot -0.25"
        else:
            detail += " → no cross rule"
        print(f"  {desc_x} ↔ {desc_y}: {detail}")

    print(f"\nTotal activity-specific score: {result}")
    assert abs(result - 0.7) < 1e-9, f"Expected 0.7, got {result}"
    print("Test passed ✓")