from .disposable import Disposable

class CompositeDisposable(Disposable):
    def __init__(self, disposables=None):
        self.disposables = disposables or []
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

        for disposable in currentDisposables:
            disposable.dispose()
            
    def clear(self):
        currentDisposables = self.disposables[:]
        self.disposables = []
        self.length = 0
        
        for disposable in currentDisposables:
            disposable.dispose()
            
    def contains(item):
        return item in self.disposables

    def toArray(self):
        return self.disposables[:]

