#! /usr/bin/env python2.7

import mysql.connector, os, subprocess, sys, tempfile
from Queue import Full, Queue
from threading import Thread

from atomicint import AtomicInt

GENERATE = 200000 # How many combos to generate?


cnx = mysql.connector.connect(user="",
                              password="",
                              host="127.0.0.1",
                              db="blackbox_production")

q = Queue(GENERATE * 10)
with open("combos", "w") as f:
    generated = AtomicInt(0)
    class Worker(Thread):
        def run(self):
            tff, tfp = tempfile.mkstemp()
            os.close(tff)
            while True:
                master_event_id, source_file_id = q.get()
                rtn = os.system("timeout -s KILL 10 /tools/nccb/bin/print-compile-input /data/compile-inputs %d %d > %s" % (source_file_id, master_event_id, tfp))
                if rtn != 0:
                    q.task_done()
                    continue
                with open(tfp) as f2:
                    if f2.read().strip() == "Searching rest":
                        q.task_done()
                        continue

                rtn = os.system("grmtools/target/release/lrlex grammars/java7/java.l %s > /dev/null 2> /dev/null" % tfp)
                if rtn != 0:
                    q.task_done()
                    continue
                out = subprocess.check_output(["../runner/java_parser_none", tfp])
                if "Parsed successfully" in out:
                    q.task_done()
                    continue

                q.task_done()
                i = generated.add(1)
                if i >= GENERATE:
                    return
                f.write("%d %d\n" % (source_file_id, master_event_id))
                f.flush()

                if i % 100 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()

    c1 = cnx.cursor()
    c1.execute("""SELECT master_events.id, compile_inputs.source_file_id
                  FROM master_events straight_join compile_events straight_join compile_inputs
                  WHERE      compile_events.success=0
                         AND master_events.event_id=compile_events.id
                         AND (compile_events.reason IS null
                              OR compile_events.reason="user")
                         AND master_events.event_type="CompileEvent"
                         AND master_events.id >= 1000000
                         AND master_events.id < 1900000000
                         AND compile_inputs.compile_event_id = compile_events.id
                  ORDER BY RAND()
               """)

    workers = []
    for _ in range(12):
        w = Worker()
        w.daemon = True
        workers.append(w)
        w.start()

    try:
        for r1 in c1:
            if generated.val() == GENERATE:
                break
            q.put(r1, block=True)
    except Exception, e:
        print e

    for w in workers:
        w.join()

    if generated.val() < GENERATE:
        sys.stderr.write("WARNING: exception happened before combos file is complete")

    print
