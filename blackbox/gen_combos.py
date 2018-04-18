#! /usr/bin/env python2.7

# Copyright (c) 2018 King's College London
# created by the Software Development Team <http://soft-dev.org/>
#
# The Universal Permissive License (UPL), Version 1.0
#
# Subject to the condition set forth below, permission is hereby granted to any
# person obtaining a copy of this software, associated documentation and/or data
# (collectively the "Software"), free of charge and under any and all copyright
# rights in the Software, and any and all patent rights owned or freely
# licensable by each licensor hereunder covering either (i) the unmodified
# Software as contributed to or provided by such licensor, or (ii) the Larger
# Works (as defined below), to deal in both
#
# (a) the Software, and
# (b) any piece of software and/or hardware listed in the lrgrwrks.txt file
# if one is included with the Software (each a "Larger Work" to which the Software
# is contributed by such licensors),
#
# without restriction, including without limitation the rights to copy, create
# derivative works of, display, perform, and distribute the Software and make,
# use, sell, offer for sale, import, export, have made, and have sold the
# Software and the Larger Work(s), and to sublicense the foregoing rights on
# either these or other terms.
#
# This license is subject to the following condition: The above copyright notice
# and either this complete permission notice or at a minimum a reference to the
# UPL must be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import mysql.connector, os, subprocess, sys, tempfile
from Queue import Full, Queue
from threading import Thread

from atomicint import AtomicInt

GENERATE = 200000 # How many combos to generate?


cnx = mysql.connector.connect(user="",
                              password="",
                              host="127.0.0.1",
                              db="blackbox_production")

q = Queue(64)
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

                rtn = os.system("lrlex/target/release/lrlex grammars/java7/java.l %s > /dev/null 2> /dev/null" % tfp)
                if rtn != 0:
                    q.task_done()
                    continue
                rtn = os.system("lrpar/target/release/lrpar -r none grammars/java7/java.l grammars/java7/java.y %s > /dev/null 2> /dev/null" % tfp)
                if rtn == 0:
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

    for _ in range(12):
        w = Worker()
        w.daemon = True
        w.start()

    for r1 in c1:
        if generated.val() < GENERATE:
            try:
                q.put(r1, timeout=1)
            except Full:
                continue

    print
