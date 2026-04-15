from activities import Activity

class Gene:
    def __init__(self, activity: Activity, time, room, facilitator):
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
if __name__ == "__main__":
    gene1 = Gene('201A', '10:00 AM', 'Beach 201', 'Shaw')
    gene2 = Gene('201B', '1:00 PM', 'Beach 201', 'Shaw')
    print(gene1.activity)

    my_schedule = Schedule()
    my_schedule.add_gene(gene1)
    my_schedule.add_gene(gene2)
    print(my_schedule.genes[0].time, my_schedule.genes[1].time)
