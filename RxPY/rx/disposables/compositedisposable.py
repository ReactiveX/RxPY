from .disposable import Disposable

class CompositeDisposable(Disposable):
    def __init__(self, *args):
        self.disposables = list(args)
        self.is_disposed = False
        self.length = len(self.disposables)

    def add(self, item):
        if self.is_disposed:
            item.dispose()
        else:
            self.disposables.append(item)
            self.length += 1

    def remove(self, item):
        should_dispose = False
        if not self.is_disposed and item in self.disposables:
            self.disposables.remove(item)
            should_dispose = True
            self.length -= 1
            item.dispose()

        return should_dispose

    def dispose(self):
        if self.is_disposed:
            return
        
        self.is_disposed = True
        current_disposables = self.disposables[:]
        self.disposables = []
        self.length = 0

        for disposable in current_disposables:
            disposable.dispose()
            
    def clear(self):
        current_disposables = self.disposables[:]
        self.disposables = []
        self.length = 0
        
        for disposable in current_disposables:
            disposable.dispose()
            
    def contains(self, item):
        return item in self.disposables

    def to_array(self):
        return self.disposables[:]

