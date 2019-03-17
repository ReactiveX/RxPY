from rx.concurrency import VirtualTimeScheduler


class MockDisposable:
    def __init__(self, scheduler: VirtualTimeScheduler):
        self.scheduler: VirtualTimeScheduler = scheduler
        self.disposes = []
        self.disposes.append(self.scheduler.clock)

    def dispose(self):
        self.disposes.append(self.scheduler.clock)
