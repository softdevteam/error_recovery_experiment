#! /usr/bin/env python2.7

import os
from os import listdir, stat
from decimal import Decimal

SRC_FILES_DIR = "src_files"

class Results:
    def __init__(self,
                 latex_name,
                 rows,
                 num_error_locs,
                 failure_rate,
                 mean_time,
                 median_time):
        self.latex_name = latex_name
        self.rows = rows
        self.num_error_locs = num_error_locs
        self.failure_rate = failure_rate
        self.mean_time = mean_time
        self.median_time = median_time

def process(latex_name, p):
    d = []
    num_error_locs = 0
    num_success = 0
    with open(p) as f:
        for l in f.readlines():
            l = l.strip()
            if len(l) == 0:
                continue
            s = l.split(", ")
            r = [s[0],
                 Decimal(s[1]),
                 True if s[2] == "1" else False,
                 int(s[3])]
            d.append(r)
            num_error_locs += r[3]
            if r[2]:
                num_success += 1

    failure_rate = (float(len(d) - num_success) / len(d)) * 100.0
    times = map(lambda x: x[1], d)
    mean_time = sum(times) / len(d)
    times.sort()
    assert(len(d) % 2 == 0)
    median_time = times[len(d) / 2]
    return Results(latex_name, d, num_error_locs, failure_rate, mean_time, median_time)

def corpus_size():
    num_files = 0
    size_bytes = 0
    for l in listdir(SRC_FILES_DIR):
        p = os.path.join(SRC_FILES_DIR, l)
        size_bytes += os.stat(p).st_size
        num_files += 1
    return num_files, size_bytes

cpctplus = process("\\cpctplus", "cpctplus.csv")
mf = process("\\mf", "mf.csv")
mfrev = process("\\mfrev", "mf_rev.csv")

with open("experimentstats.tex", "w") as f:
    num_files, size_bytes = corpus_size()
    f.write(r"\newcommand{\corpussize}{\numprint{%s}\xspace}" % str(num_files))
    f.write("\n")
    f.write(r"\newcommand{\corpussizemb}{\numprint{%s}\xspace}" % str(size_bytes / 1024 / 1024))
    f.write("\n")
    for x in [cpctplus, mf, mfrev]:
        f.write(r"\newcommand{%ssuccessrate}{%.2f\%%\xspace}" % (x.latex_name, 100.0 - x.failure_rate))
        f.write("\n")
        f.write(r"\newcommand{%sfailurerate}{%.2f\%%\xspace}" % (x.latex_name, x.failure_rate))
        f.write("\n")
        f.write(r"\newcommand{%smeantime}{%.5fs\xspace}" % (x.latex_name, x.mean_time))
        f.write("\n")
        f.write(r"\newcommand{%smediantime}{%.5fs\xspace}" % (x.latex_name, x.median_time))
        f.write("\n")
        f.write(r"\newcommand{%serrorlocs}{\numprint{%s}\xspace}" % (x.latex_name, x.num_error_locs))
        f.write("\n")

    mf_cpctplus_ratio = (mf.failure_rate / cpctplus.failure_rate) * 100.0
    f.write(r"\newcommand{\mfcpctplusfailurerateratio}{%.2f\%%\xspace}" % mf_cpctplus_ratio)
    f.write("\n")

    mfrev_mf_ratio = (float(mfrev.num_error_locs - mf.num_error_locs) / mf.num_error_locs) * 100.0
    f.write(r"\newcommand{\mfreverrorlocsratioovermf}{%.2f\%%\xspace}" % mfrev_mf_ratio)
    f.write("\n")

with open("table.tex", "w") as f:
    for x in [cpctplus, mf, mfrev]:
        f.write("%s & %.5f & %.5f & %.2f & \\numprint{%d} \\\\\n" % (x.latex_name, x.mean_time, x.median_time, x.failure_rate, x.num_error_locs))
