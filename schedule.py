# schedule

class Gene:
    def __init__(self, activity, time, room, facilitator):
        self.activity = activity
        self.time = time
        self.room = room
        self.facilitator = facilitator

# check
my_gene = Gene('201A', '10AM', 'Beach201', 'Shaw')
print(my_gene.time)

class Schedule:
    def __init__(self):
        # always in this order
        self.genes = {"SLA101A": [],
                      "SLA101B": [],
                      "SLA191A": [],
                      "SLA191B": [],
                      "SLA201": [],
                      "SLA291": [],
                      "SLA303": [],
                      "SLA304": [],
                      "SLA394": [],
                      "SLA449": [],
                      "SLA451": []
                      }

    def add_gene(self, gene):
        self.genes.update({gene.activity: [gene.time, gene.room, gene.facilitator]})

# check
my_schedule = Schedule()
my_schedule.add_gene(my_gene)
print(my_schedule.genes[my_gene.activity])