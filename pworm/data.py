"""
 
"""
class Stack :    
    def __init__(self, max = -1):
        self._list = []
        self._max = max

    def get(self) :
        if 0 == len(self._list):
            raise IndexError()
        return self._list.pop()

    def put(self, *values):
        if self._max > 0 and self.size() + len(values) > self._max :
            raise IndexError()
        for value in values :
            self._list.append(value)

    def peek(self) :
        if 0 == len(self._list):
            raise IndexError()
        return self._list[-1]
    
    def size(self):
        return len(self._list)

class Queue(Stack) :
    def get(self) :
        if 0 == len(self._list):
            raise IndexError()
        return self._list.pop(0)    

    def peek(self) :
        if 0 == len(self._list):
            raise IndexError()
        return self._list[0]

    def last(self) :
        return super().peek()


    