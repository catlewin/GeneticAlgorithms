# class for activities
# Each activity has a name, expected enrollment, a list of preferred facilitators, and other facilitators

class Activity:
    def __init__(self, name: str, enrollment: int, preferred: list[str], other: list[str]):
        self.name = name
        self.enrollment = enrollment
        self.preferred = preferred
        self.other = other



activity_101A = Activity(name="101 A", enrollment=40, preferred=['Glen', 'Lock', 'Banks'],
                                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
activity_101B = Activity('101 B', enrollment=35, preferred=['Glen', 'Lock', 'Banks'],
                                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
activity_191A = Activity("191 A", enrollment=45, preferred=['Glen', 'Lock', 'Banks'],
                                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
activity_191B = Activity("191 B", enrollment=40, preferred=['Glen', 'Lock', 'Banks'],
                                         other=['Numen', 'Richards', 'Shaw', 'Singer'])
activity_201 = Activity("201", enrollment=60, preferred=['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'],
                                         other=['Richards', 'Uther', 'Shaw'])
activity_291 = Activity("291", enrollment=50, preferred=['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'],
                                         other=['Richards', 'Uther', 'Shaw'])
activity_303 = Activity("303", enrollment=25, preferred=['Glen', 'Zeldin'],
                                         other=['Banks'])
activity_304 = Activity("304", enrollment=20, preferred=['Singer', 'Uther'],
                                         other=['Richards'])
activity_394 = Activity("394", enrollment=15, preferred=['Tyler', 'Singer'],
                                         other=['Richards', 'Zeldin'])
activity_449 = Activity("449", enrollment=30, preferred=['Tyler', 'Zeldin', 'Uther'],
                                         other=['Shaw', 'Zeldin'])
activity_451 = Activity("451", enrollment=90, preferred=['Lock', 'Zeldin', 'Banks'],
                                         other=['Tyler', 'Singer', 'Shaw', 'Glen'])

activities = {
    '101 A': activity_101A,
    '101 B': activity_101B,
    '191 A': activity_191A,
    '191 B': activity_191B,
    '201': activity_201,
    '291': activity_291,
    '291A': activity_291,
    '303': activity_303,
    '304': activity_304,
    '394': activity_394,
    '449': activity_449,
    '451': activity_451,
}
