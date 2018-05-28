#! /usr/bin/env python2.7

import os, re, sys, time
from subprocess import Popen
from tempfile import TemporaryFile

RE_BUDGET = re.compile("^recovery budget ([0-9.]+)", re.MULTILINE)
RE_COST = re.compile("^repair cost ([0-9.]+)", re.MULTILINE)
RE_RECOVERY_POINTS = re.compile("^Error at line", re.MULTILINE)
BUDGET = 0.5
PEXECS = 30

src_files, binary, recoverer, yaccp, lexp, outp = sys.argv[1:7]

assert not os.path.exists(outp)

times = []
failures = 0
i = 0
with open(outp, "w") as outf:
    for j in range(PEXECS):
        for l in os.listdir(src_files):
            i += 1
            if i % 100 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            if i % 1000 == 0:
                # Let the machine have a chance to cool down every so often
                time.sleep(10)
            p = os.path.join(src_files, l)
            with TemporaryFile() as tmpf:
                lrpar = Popen([binary, "-r", recoverer, yaccp, lexp, p], stdout=tmpf)
                lrpar.wait()
                tmpf.seek(0, os.SEEK_SET)
                output = tmpf.read()
                m = RE_BUDGET.search(output)
                remaining = float(m.group(1))
                spent = BUDGET - remaining
                if "No repairs found" in output:
                    failures += 1
                    f = "0"
                    costs = ""
                else:
                    f = "1"
                    costs_l = []
                    for m in RE_COST.finditer(output):
                        costs_l.append(m.group(1))
                    assert(len(costs_l) == len(list(RE_RECOVERY_POINTS.finditer(output))))
                    costs = ":".join(costs_l)
                # CSV fields, in order:
                #   bench name,
                #   run number,
                #   time spent recovering (secs)
                #   succeeded recovering (0: failed, 1: succeeded)
                #   cost of each repair point found (separated by ":" and only
                #                                    meaningful if succeeded recovering == 1)
                outf.write("%s, %s, %.10f, %s, %s\n" % (l, j, spent, f, costs))
                outf.flush()
                times.append(spent)

print
print "Average:", sum(times) / len(times)
times.sort()
print "Median:", times[len(times) / 2]
print "#Failed to repair: %d (%.3f%%)" % (failures, (float(failures) / len(times)) * 100.0)
