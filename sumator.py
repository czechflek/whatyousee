import collections as c
import time
from threading import Thread


class Sumator:
    def __init__(self, map):
        self.alive = False
        self.map = map.get_array()
        self.queue = c.deque()

    def start_service(self):
        self.alive = True
        t = Thread(target=self.sumator)
        t.daemon = False
        t.start()

    def stop_service(self):
        self.alive = False

    def add_task(self, task):
        self.queue.appendleft(task)

    def sumator(self):
        while self.alive:
            if self.queue:
                task = self.queue.pop()
                self.map[task[0]][task[1]] += task[2]
            else:
                time.sleep(0.001)
