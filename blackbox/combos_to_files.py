#! /usr/bin/env python

import os, sys
from Queue import Queue
from threading import Thread

from atomicint import AtomicInt

q = Queue(512)
done = AtomicInt(0)
class Worker(Thread):
    def run(self):
        i = 0
        while True:
            l = q.get()
            i = done.add(1)
            if i % 100 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            a, b = l.strip().split(" ")
            os.system("/tools/nccb/bin/print-compile-input /data/compile-inputs %s %s > src_files/%s_%s" % (a, b, a, b))
            q.task_done()

for _ in range(12):
    w = Worker()
    w.daemon = True
    w.start()

with open("combos", "r") as f:
    for l in f:
        q.put(l)

    q.join()
    print
