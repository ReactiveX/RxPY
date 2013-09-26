# Collections
class IndexedItem(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value

    def compare_to(self, other):
        c = self.value.compare_to(other.value)
        if not c:
            c = self.id - other.id        
        return c

class PriorityQueue(object):
    """ Priority Queue for Scheduling"""
    count = 0

    def __init__(self, capacity):
        self.items = []
        self.length = 0
    
    def is_higher_priority(self, left, right):
        return self.items[left].compare_to(self.items[right]) < 0

    def percolate(self, index):
        if index >= self.length or index < 0:
            return
        
        parent = index - 1 >> 1
        if parent < 0 or parent == index:
            return
        
        if self.is_higher_priority(index, parent):
            temp = self.items[index]
            self.items[index] = self.items[parent]
            self.items[parent] = temp
            self.percolate(parent)
        
    def heapify(self, index=None):
        if index is None:
            index = 0;
        
        if index >= self.length or index < 0:
            return
        
        left = 2 * index + 1
        right = 2 * index + 2
        first = index
        
        if left < self.length and self.is_higher_priority(left, first):
            first = left
        
        if right < self.length and self.is_higher_priority(right, first):
            first = right
        
        if first != index:
            temp = self.items[index]
            self.items[index] = self.items[first]
            self.items[first] = temp
            self.heapify(first)

    def peek(self):
        return self.items[0].value
    
    def remove_at(self, index):
        self.length -= 1
        self.items[index] = self.items[self.length]
        del self.items[self.length]
        self.heapify()
    
    def dequeue(self):
        result = self.peek()
        self.remove_at(0)
        return result
    
    def enqueue(self, item):
        index = self.length
        self.length += 1
        self.items.append(IndexedItem(PriorityQueue.count, item))
        PriorityQueue.count += 1
        self.percolate(index)
    
    def remove(self, item):
        for index, _item in enumerate(self.items):
            if _item.value == item:
                self.remove_at(index)
                return True
        
        return False
