from activities import Activity
from rooms import Room

class Gene:
    def __init__(self, activity: Activity, time, room: Room, facilitator):
        self.activity = activity
        self.time = time
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
    room1 = Room(name='Beach', room = 201, capacity=18)
    activity1 = Activity(name='SLA101A', enrollment=40, preferred=['Glen', 'Lock', 'Banks'],
                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
    gene1 = Gene(activity1, '10:00 AM', room1, 'Shaw')
    room2 = Room(name='Beach', room=301, capacity=25)
    activity2 = Activity(name='SLA101B', enrollment=35, preferred=['Glen', 'Lock', 'Banks'],
                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
    gene2 = Gene(activity2, '1:00 PM', room2, 'Shaw')
    print(gene1.activity.name)

    my_schedule = Schedule()
    my_schedule.add_gene(gene1)
    my_schedule.add_gene(gene2)
    print(my_schedule.genes[0].time, my_schedule.genes[1].time)
