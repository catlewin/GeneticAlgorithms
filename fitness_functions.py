from itertools import combinations
from schedule import Schedule
from cs_activity_specific_adjustments import hour_gap

def check_room_overlap(schedule: Schedule):
    """Penalize -0.5 for each pair of activities sharing the same room and time slot."""
    for geneA, geneB in combinations(schedule.genes, 2):
        if geneA.room == geneB.room and geneA.time == geneB.time:
            schedule.fitness -= 0.5

def check_room_size(schedule: Schedule):
    """
        Penalize or reward based on how well the room capacity fits enrollment:
          - Room too small (capacity < enrollment):        -0.5
          - Room > 3x enrollment:                          -0.4
          - Room > 1.5x enrollment:                        -0.2
          - Appropriate size:                              +0.3
        """
    for gene in schedule.genes:
        capacity = gene.room.capacity
        enrollment = gene.activity.enrollment
        if capacity < enrollment: # room too small
            schedule.fitness -= 0.5
        elif capacity > (enrollment * 3): # room x3 enrollment
            schedule.fitness -= 0.4
        elif capacity > (enrollment * 1.5): # room x1.5 enrollment
            schedule.fitness -= 0.2
        else: # appropriate size
            schedule.fitness += 0.3

# Activities is overseen by a preferred facilitator: + 0.5
def check_facilitator(schedule: Schedule):
    """
        Reward/penalize based on facilitator preference:
          - Preferred facilitator:  +0.5
          - Other facilitator:      +0.2
          - Neither:                -0.1
        """
    for gene in schedule.genes:
        assigned = gene.facilitator
        if assigned in gene.activity.preferred:
            schedule.fitness += 0.5
        elif assigned in gene.activity.other:
            schedule.fitness += 0.2
        else:
            schedule.fitness -= 0.1

def check_facilitator_load(schedule: Schedule):
    """
        For each facilitator:
          - Scheduled for 2+ activities at the same time:     -0.2 per conflict
          - Consecutive activities where one is Roman/Beach:  -0.4
          - Consecutive activities (normal rooms):            +0.5
          - Teaching > 4 activities total:                    -0.5
          - Teaching < 2 activities (< 1 for Tyler):          -0.2
          - No time conflicts:                                +0.2
        """
    facilitators = ['Glen', 'Lock', 'Banks', 'Numen', 'Richards',
                    'Shaw', 'Singer', 'Zeldin', 'Uther', 'Tyler']

    for facilitator in facilitators:
        fac_genes = [a for a in schedule.genes if a.facilitator == facilitator] # list of activities the facilitator leads
        activity_count = len(fac_genes)
        has_overlap = False

        for geneA, geneB in combinations(fac_genes, 2):
            if geneA.time == geneB.time: # overlapping activities
                schedule.fitness -= 0.2
                has_overlap = True
            elif hour_gap(geneA.time, geneB.time) == 1: # consecutive classes
                if geneA.room.name in ['Roman', 'Beach'] or geneB.room.name in ['Roman', 'Beach']:
                    schedule.fitness -= 0.4
                else:
                    schedule.fitness += 0.5

        if activity_count > 4:
            schedule.fitness -= 0.5
        elif activity_count < 3:
            if not (facilitator == 'Tyler' and activity_count < 2):
                schedule.fitness -= 0.2

        if not has_overlap:
            schedule.fitness += 0.2


def evaluate_fitness(schedule: Schedule):
    """Run all fitness checks on a schedule."""
    schedule.fitness = 0.0
    check_room_overlap(schedule)
    check_room_size(schedule)
    check_facilitator(schedule)
    check_facilitator_load(schedule)
