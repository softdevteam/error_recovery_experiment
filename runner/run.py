#! /usr/bin/env python2.7

import os, re, sys
from subprocess import Popen
from tempfile import TemporaryFile

RE_BUDGET = re.compile("recovery budget ([0-9.]+)")
RE_RECOVERY_POINTS = re.compile("^Error at line", re.MULTILINE)
BUDGET = 0.5

src_files, binary, recoverer, yaccp, lexp, outp = sys.argv[1:7]

assert not os.path.exists(outp)

times = []
failures = 0
i = 0
with open(outp, "w") as outf:
    for l in os.listdir(src_files):
        i += 1
        if i % 10 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
        p = os.path.join(src_files, l)
        with TemporaryFile() as tmpf:
            lrpar = Popen([binary, "-r", recoverer, yaccp, lexp, p], stdout=tmpf)
            lrpar.wait()
            tmpf.seek(0, os.SEEK_SET)
            output = tmpf.read()
            num_recovery_points = len(list(RE_RECOVERY_POINTS.finditer(output)))
            m = RE_BUDGET.match(output)
            remaining = float(m.group(1))
            spent = BUDGET - remaining
            if "No repairs found" in output:
                failures += 1
                f = "0"
            else:
                f = "1"
            # CSV fields (in order:
            #   bench name,
            #   time spent recovering (secs)
            #   succeeded recovering (0: failed, 1: succeeded)
            #   num repair points found
            outf.write("%s, %.10f, %s, %s\n" % (l, spent, f, num_recovery_points))
            times.append(spent)

print
print "Average:", sum(times) / len(times)
times.sort()
print "Median:", times[len(times) / 2]
print "#Failed to repair: %d (%.3f%%)" % (failures, (float(failures) / len(times)) * 100.0)
