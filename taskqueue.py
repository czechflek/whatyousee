import Queue
from threading import Thread


class TaskQueue(Queue.Queue):
    def __init__(self, num_workers=1):
        Queue.Queue.__init__(self)
        self.alive = True
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, task, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((task, args, kwargs))

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def stop_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while self.alive:
            tupl = self.get()
            item, args, kwargs = self.get()
            item(*args, **kwargs)
            self.task_done()
