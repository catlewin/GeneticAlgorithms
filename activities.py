# class for activities
# Each activity has a name, expected enrollment, a list of preferred facilitators, and other facilitators

class Activity:
    def __init__(self, name: str, enrollment: int, preferred: list[str], other: list[str]):
        self.name = name
        self.enrollment = enrollment
        self.preferred = preferred
        self.other = other

