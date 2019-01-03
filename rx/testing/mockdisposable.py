class MockDisposable:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.disposes = []
        self.disposes.append(self.scheduler.clock)

    def dispose(self):
        self.disposes.append(self.scheduler.clock)
