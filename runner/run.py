#! /usr/bin/env python2.7

import os, re, sys, time
from subprocess import Popen
from tempfile import TemporaryFile

RE_BUDGET = re.compile("^recovery budget ([0-9.]+)", re.MULTILINE)
RE_COST = re.compile("^repair cost ([0-9.]+)", re.MULTILINE)
RE_RECOVERY_POINTS = re.compile("^Error at line", re.MULTILINE)
RE_LEXEME_COUNT = re.compile("^Lexeme count: ([0-9]+)", re.MULTILINE)
RE_SKIPPED = re.compile("^Input skipped: ([0-9]+)", re.MULTILINE)
PEXECS = 30

src_files, binary, budget, outp = sys.argv[1:5]
budget = float(budget)

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
            if i % 10000 == 0:
                # Let the machine have a chance to cool down every so often
                time.sleep(10)
            p = os.path.join(src_files, l)
            with TemporaryFile() as tmpf:
                lrpar = Popen([binary, p], stdout=tmpf)
                lrpar.wait()
                tmpf.seek(0, os.SEEK_SET)
                output = tmpf.read()
                m = RE_BUDGET.search(output)
                remaining = float(m.group(1))
                spent = budget - remaining
                if "Parsing did not complete" in output:
                    failures += 1
                    f = "0"
                else:
                    f = "1"

                if binary == "java_parser_panic":
                    costs = ""
                else:
                    costs_l = []
                    for m in RE_COST.finditer(output):
                        costs_l.append(m.group(1))
                    costs = ":".join(costs_l)

                error_locs = len(list(RE_RECOVERY_POINTS.finditer(output)))
                lexeme_count = RE_LEXEME_COUNT.search(output).group(1)
                skipped = RE_SKIPPED.search(output).group(1)
                # CSV fields, in order:
                #   bench name
                #   run number
                #   time spent recovering (secs)
                #   succeeded recovering (0: failed, 1: succeeded)
                #   number of error locations
                #   cost of each repair point found (separated by ":" and only
                #     meaningful if succeeded recovering == 1)
                #   number of lexemes in file
                #   number of lexemes not parsed (either because of Del repairs, or because
                #     the recoverer could not repair the remainder of a file)
                outf.write("%s, %s, %.10f, %s, %s, %s, %s, %s\n" %
                           (l, j, spent, f, error_locs, costs, lexeme_count, skipped))
                outf.flush()
                times.append(spent)

print
print "Average:", sum(times) / len(times)
times.sort()
print "Median:", times[len(times) / 2]
print "#Failed to repair: %d (%.3f%%)" % (failures, (float(failures) / len(times)) * 100.0)
