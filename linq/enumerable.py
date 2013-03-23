import sys

class Enumerable(object):
    def __init__(self, iterator):
        self._iterator = iterator
        
    def __iter__(self):
        return  self._iterator.__iter__()

    def where(self, predicate):
        return Enumerable(value for value in self if predicate(value))

    def select(self, selector):
        return Enumerable(selector(value) for value in self)

    def take(self, count):
        def iterator():
            n = count

            for value in self:
                if n <= 0:
                    raise StopIteration
                n -= 1
                yield value
            
            raise StopIteration
            
        return Enumerable(iterator())   

    def first(self):
        pass

    def last(self):
        pass

    @classmethod
    def range(cls, start, count):
        def iterator():
            value = start
            n = count
            while n > 0:
                yield value
                value += 1
                n -= 1

            raise StopIteration

        return cls(iterator())

    @classmethod
    def repeat(cls, element, count):
        return cls(element for _ in range(count))

def main():
    #a = Enumerable(iter([1,2,30]))
    a = Enumerable.range(0, sys.maxsize)
    #a = Enumerable.repeat(10, sys.maxint)
    #a = (a
    #    .where(lambda x: x > 3)
    #    .select(lambda x: x * 10)
    #    )

    a = a \
        .where(lambda x: x > 3) \
        .select(lambda x: x * 10)

    a = a.take(100)

    # a.where([x for x in xs ])
    
    b = a.__iter__()
    print(list(b))
    #print b.to_array()

if __name__ == '__main__':
    main()