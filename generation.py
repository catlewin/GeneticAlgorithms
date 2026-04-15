from schedule import Schedule


class Generation:
    def __init__(self, generation: list[Schedule]):
        self.generation = generation
        self.best_fit = None
        self.avg_fit = None
        self.worst_fit = None
        self.gen_improvement = None