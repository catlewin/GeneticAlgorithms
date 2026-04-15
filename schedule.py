from datetime import time as t

class Gene:
    def __init__(self, activity, time: t, room, facilitator):
        #FLAG: can replace string activity with activity class once implemented
        self.activity = activity
        self.time = time
        #FLAG: can replace string room with room class once implemented
        self.room = room
        self.facilitator = facilitator

class Schedule:
    def __init__(self):
        # always in this order
        self.genes = []
        self.fitness = 0.0
    def add_gene(self, gene: Gene):
        self.genes.append(gene)

# check
gene1 = Gene('201A', t(10), 'Beach201', 'Shaw')
gene2 = Gene('201B', t(13), 'Beach201', 'Shaw')
print(gene1.activity)

my_schedule = Schedule()
my_schedule.add_gene(gene1)
my_schedule.add_gene(gene2)
print(my_schedule.genes[0].time, my_schedule.genes[1].time)