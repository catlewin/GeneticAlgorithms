# schedule

class Gene:
    def __init__(self, activity, time, room, facilitator):
        self.activity = activity
        self.time = time
        self.room = room
        self.facilitator = facilitator
        self.fitness = 0.0

# check
gene1 = Gene('201A', '10AM', 'Beach201', 'Shaw')
gene2 = Gene('201B', '10AM', 'Beach201', 'Shaw')
print(gene1.activity)

class Schedule:
    def __init__(self):
        # always in this order
        self.genes = []

    def add_gene(self, gene):
        self.genes.append(gene)

# check
my_schedule = Schedule()
my_schedule.add_gene(gene1)
my_schedule.add_gene(gene2)
print(my_schedule.genes[0].activity, my_schedule.genes[1].activity)