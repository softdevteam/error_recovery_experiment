from threading import Lock

class AtomicInt:
    def __init__(self, v):
        self.v = v
        self._lock = Lock()

    def add(self, i):
        with self._lock:
            o = self.v
            self.v = o + i
        return o

    def val(self):
        with self._lock:
            return self.v
