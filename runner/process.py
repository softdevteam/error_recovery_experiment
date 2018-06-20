#! /usr/bin/env python2.7

import math, random, os, sys
from os import listdir, stat
from decimal import Decimal
import decimal

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = [r'\usepackage[cm]{sfmath}']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = 'cm'
matplotlib.rcParams.update({'errorbar.capsize': 2})
from matplotlib.ticker import ScalarFormatter
import matplotlib.patches as mpatches
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from numpy import histogram

from pykalibera.data import confidence_slice

SRC_FILES_DIR = "src_files"
BOOTSTRAP = 10000
HISTOGRAM_BINS = 75
ERROR_LOCS_HISTOGRAM_BINS = 50
MAX_RECOVERY_TIME = 0.5

class PExec:
    def __init__(self,
                 name,
                 run_num,
                 recovery_time,
                 succeeded,
                 costs):
        self.name = name
        self.run_num = run_num
        self.recovery_time = recovery_time
        self.succeeded = succeeded
        self.costs = costs

class Results:
    def __init__(self,
                 latex_name,
                 pexecs,
                 num_runs):
        self.latex_name = latex_name
        benches = {}
        for p in pexecs:
            if p.name not in benches:
                benches[p.name] = []
            benches[p.name].append(p)
        self.pexecs = list(benches.values())
        self.num_runs = num_runs

        sys.stdout.write("%s: recovery_times..." % latex_name)
        sys.stdout.flush()
        self.recovery_time_mean_ci = confidence_slice(self.bootstrap_recovery_means(), "0.99")
        self.recovery_time_median_ci = confidence_slice(self.bootstrap_recovery_medians(), "0.99")
        sys.stdout.write(" failure rates...")
        sys.stdout.flush()
        self.failure_rate_ci = confidence_slice(self.bootstrap_failure_rates(), "0.99")
        sys.stdout.write(" error locations...")
        sys.stdout.flush()
        self.error_locs_ci = confidence_slice(self.bootstrap_error_locs(), "0.99")
        sys.stdout.write(" costs...")
        sys.stdout.flush()
        self.costs_ci = confidence_slice(self.bootstrap_costs(), "0.99")
        print

    def bootstrap_recovery_means(self):
        out = []
        for i in range(BOOTSTRAP):
            means = []
            for pexecs in self.pexecs:
                pexec = random.choice(pexecs)
                means.append(pexec.recovery_time)
            out.append(mean(means))
        return out

    def bootstrap_recovery_medians(self):
        out = []
        for i in range(BOOTSTRAP):
            means = []
            for pexecs in self.pexecs:
                pexec = random.choice(pexecs)
                means.append(pexec.recovery_time)
            out.append(median(means))
        return out

    def bootstrap_failure_rates(self):
        out = []
        for i in range(BOOTSTRAP):
            failures = 0
            for pexecs in self.pexecs:
                pexec = random.choice(pexecs)
                if not pexec.succeeded:
                    failures += 1
            out.append((float(failures) / float(len(self.pexecs))) * 100.0)
        return out

    def bootstrap_error_locs(self):
        out = []
        for i in range(BOOTSTRAP):
            error_locs = 0
            for pexecs in self.pexecs:
                pexec = random.choice(pexecs)
                error_locs += len(pexec.costs)
            out.append(error_locs)
        return out

    def bootstrap_costs(self):
        out = []
        for i in range(BOOTSTRAP):
            costs = []
            for pexecs in self.pexecs:
                pexec = random.choice(pexecs)
                if pexec.succeeded:
                    costs.extend(pexec.costs)
            if len(costs) > 0:
                out.append(mean(costs))
        return out

def confidence_ratio_recovery_means(x, y):
    xmeans = x.bootstrap_recovery_means()
    ymeans = y.bootstrap_recovery_means()
    out = []
    for a, b in zip(xmeans, ymeans):
        out.append(float(a / b) * 100.0)
    return confidence_slice(out, "0.99")

def confidence_ratio_error_locs(x, y):
    xmeans = x.bootstrap_error_locs()
    ymeans = y.bootstrap_error_locs()
    out = []
    for a, b in zip(xmeans, ymeans):
        out.append((float(a - b) / float(b)) * 100.0)
    return confidence_slice(out, "0.99")

def mean(l):
    return float(sum(l) / Decimal(len(l)))

def median(l):
    l.sort()
    if len(l) % 2 == 0:
        return mean([l[len(l) // 2 - 1], l[len(l) // 2]])
    else:
        return l[len(l) // 2]

def process(latex_name, p):
    pexecs = []
    num_error_locs = 0
    num_success = 0
    max_run_num = 0
    with open(p) as f:
        for l in f.readlines():
            l = l.strip()
            if len(l) == 0:
                continue
            s = [x.strip() for x in l.split(",")]
            if s[3] == "1":
                succeeded = True
            else:
                assert s[3] == "0"
                succeeded = False
            costs = [int(x) for x in s[4].split(":") if x != ""]
            pexec = PExec(s[0], int(s[1]), Decimal(s[2]), succeeded, costs)
            max_run_num = max(max_run_num, pexec.run_num)
            pexecs.append(pexec)

    return Results(latex_name, pexecs, max_run_num + 1)

def corpus_size():
    num_files = 0
    size_bytes = 0
    for l in listdir(SRC_FILES_DIR):
        p = os.path.join(SRC_FILES_DIR, l)
        size_bytes += os.stat(p).st_size
        num_files += 1
    return num_files, size_bytes

def time_histogram(run, p):
    bbins = [[] for _ in range(HISTOGRAM_BINS)]
    bin_width = MAX_RECOVERY_TIME / HISTOGRAM_BINS
    for _ in range(BOOTSTRAP):
        d = [float(random.choice(pexecs).recovery_time) for pexecs in run.pexecs]
        hbins, _ = histogram(d, bins=HISTOGRAM_BINS, range=(0, MAX_RECOVERY_TIME))
        for i, cnt in enumerate(hbins):
            bbins[i].append(cnt)

    bins = []
    errs = []
    for bbin in bbins:
        ci = confidence_slice(bbin, "0.99")
        bins.append(ci.median)
        errs.append(int(ci.error))

    sns.set(style="whitegrid")
    plt.rc('text', usetex=True)
    plt.rc('font', family='sans-serif')
    fig, ax = plt.subplots(figsize=(8, 4))
    plt.bar(range(HISTOGRAM_BINS), bins, yerr=errs, align="center", log=True, color="#777777", \
            error_kw={"ecolor": "black", "elinewidth": 1, "capthick": 0.5, "capsize": 1})
    ax.set_xlabel('Recovery time (s)')
    ax.set_ylabel('Number of files (log$_{10}$)')
    ax.grid(linewidth=0.25)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.xlim(xmin=-.2, xmax=HISTOGRAM_BINS)
    locs = []
    labs = []
    for i in range(0, 6):
        locs.append((HISTOGRAM_BINS / 5) * i - 0.5)
        labs.append(i / 10.0)
    plt.xticks(locs, labs)
    yticks = []
    i = len(run.pexecs)
    while i >= 10:
        yticks.append(i)
        i /= 10
    plt.yticks(yticks, [str(x) for x in yticks])
    formatter = ScalarFormatter()
    formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(formatter)
    plt.savefig(p, format="pdf")

def calc_max_error_locs(run):
    n = 0
    for pexecs in run.pexecs:
        for pexec in pexecs:
            n = max(n, len(pexec.costs))
    return n

def flat_zip(x, y):
    assert len(x) == len(y)
    out = []
    for z in zip(x, y):
        out.extend(z)
    return out

def error_locs_histogram(run1, run2, p, zoom=None):
    def bins_errs(run, num_bins, max_error_locs):
        bbins = [[] for _ in range(num_bins)]
        bin_width = max_error_locs / num_bins
        for _ in range(BOOTSTRAP):
            d = [len(random.choice(pexecs).costs) for pexecs in run.pexecs]
            if zoom is not None:
                d = filter(lambda x: x <= zoom, d)
            hbins, _ = histogram(d, bins=num_bins, range=(0, max_error_locs))
            for i, cnt in enumerate(hbins):
                bbins[i].append(cnt)

        bins = []
        errs = []
        for bbin in bbins:
            ci = confidence_slice(bbin, "0.99")
            bins.append(ci.median)
            errs.append(int(ci.error))

        return bins, errs

    if zoom is None:
        max_error_locs = max(calc_max_error_locs(run1), calc_max_error_locs(run2))
    else:
        max_error_locs = zoom
    run1_bins, run1_errs = bins_errs(run1, ERROR_LOCS_HISTOGRAM_BINS, max_error_locs)
    run2_bins, run2_errs = bins_errs(run2, ERROR_LOCS_HISTOGRAM_BINS, max_error_locs)

    sns.set(style="whitegrid")
    plt.rc('text', usetex=True)
    plt.rc('font', family='sans-serif')
    fig, ax = plt.subplots(figsize=(8, 4))
    barlist = plt.bar(range(ERROR_LOCS_HISTOGRAM_BINS * 2), flat_zip(run1_bins, run2_bins), yerr=flat_zip(run1_errs, run2_errs), \
            align="center", log=True, color=["black", "red"], \
            error_kw={"ecolor": "black", "elinewidth": 1, "capthick": 0.5, "capsize": 1})
    for i in range(0, len(barlist), 2):
        barlist[i].set_color("#777777")
        barlist[i + 1].set_color("#BBBBBB")
    mf_patch = mpatches.Patch(color="#777777", label=r"\textrm{MF}")
    mfrev_patch = mpatches.Patch(color="#BBBBBB", label=r"\textrm{MF}$_{\textrm{rev}}$")
    plt.legend(handles=[mf_patch, mfrev_patch])
    ax.set_xlabel('Recovery error locations')
    ax.set_ylabel('Number of files (log$_{10}$)')
    ax.grid(linewidth=0.25)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.xlim(xmin=-.7, xmax=ERROR_LOCS_HISTOGRAM_BINS * 2)
    locs = []
    labs = []
    for i in range(0, 8):
        locs.append((ERROR_LOCS_HISTOGRAM_BINS / 7) * i * 2 - 0.5)
        labs.append(int(round((max_error_locs / 7.0) * i)))
    plt.xticks(locs, labs)
    yticks = []
    i = len(run1.pexecs)
    while i >= 10:
        yticks.append(i)
        i /= 10
    plt.yticks(yticks, [str(x) for x in yticks])
    formatter = ScalarFormatter()
    formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(formatter)
    plt.savefig(p, format="pdf")

decimal.getcontext().prec = 12
cpctplus = process("\\cpctplus", "cpctplus.csv")
mf = process("\\mf", "mf.csv")
mfrev = process("\\mfrev", "mf_rev.csv")
assert cpctplus.num_runs == mf.num_runs == mfrev.num_runs

with open("experimentstats.tex", "w") as f:
    f.write(r"\newcommand{\numruns}{\numprint{%s}\xspace}" % str(cpctplus.num_runs))
    f.write("\n")
    f.write(r"\newcommand{\numbootstrap}{\numprint{%s}\xspace}" % str(BOOTSTRAP))
    f.write("\n")
    num_files, size_bytes = corpus_size()
    f.write(r"\newcommand{\corpussize}{\numprint{%s}\xspace}" % str(num_files))
    f.write("\n")
    f.write(r"\newcommand{\corpussizemb}{\numprint{%s}\xspace}" % str(size_bytes / 1024 / 1024))
    f.write("\n")
    for x in [cpctplus, mf, mfrev]:
        f.write(r"\newcommand{%ssuccessrate}{%.2f\%%{\footnotesize$\pm$%.2f\%%}\xspace}" % \
                (x.latex_name, 100.0 - x.failure_rate_ci.median, x.failure_rate_ci.error))
        f.write("\n")
        f.write(r"\newcommand{%sfailurerate}{%.2f\%%{\footnotesize$\pm$%.2f\%%}\xspace}" % \
                (x.latex_name, x.failure_rate_ci.median, x.failure_rate_ci.error))
        f.write("\n")
        f.write(r"\newcommand{%smeantime}{%.4fs{\footnotesize$\pm$%.4fs}\xspace}" % \
                (x.latex_name, x.recovery_time_mean_ci.median, x.recovery_time_mean_ci.error))
        f.write("\n")
        f.write(r"\newcommand{%smediantime}{%.4fs{\footnotesize$\pm$%.4fs}\xspace}" % \
                (x.latex_name, x.recovery_time_median_ci.median, x.recovery_time_median_ci.error))
        f.write("\n")
        f.write(r"\newcommand{%serrorlocs}{\numprint{%s}{\footnotesize$\pm$\numprint{%s}}\xspace}" % \
                (x.latex_name, x.error_locs_ci.median, x.error_locs_ci.error))
        f.write("\n")

    mf_cpctplus_ratio_ci = confidence_ratio_recovery_means(mf, cpctplus)
    f.write(r"\newcommand{\mfcpctplusfailurerateratio}{%.1f\%%{\footnotesize$\pm$%.1f\%%}\xspace}" % \
            (mf_cpctplus_ratio_ci.median, mf_cpctplus_ratio_ci.error))
    f.write("\n")

    mfrev_mf_ratio_ci = confidence_ratio_error_locs(mfrev, mf)
    f.write(r"\newcommand{\mfreverrorlocsratioovermf}{%.1f\%%{\footnotesize$\pm$%.2f\%%}\xspace}" % \
            (mfrev_mf_ratio_ci.median, mfrev_mf_ratio_ci.error))
    f.write("\n")

with open("table.tex", "w") as f:
    for x in [cpctplus, mf, mfrev]:
        f.write("%s & %.4f{\scriptsize$\pm$%.5f} & %.6f{\scriptsize$\pm$%.7f} & %.2f{\scriptsize$\pm$%.3f}& %.2f{\scriptsize$\pm$%.3f} & \\numprint{%d}{\scriptsize$\pm$%s} \\\\\n" % \
                (x.latex_name, \
                 x.recovery_time_mean_ci.median, x.recovery_time_mean_ci.error, \
                 x.recovery_time_median_ci.median, x.recovery_time_median_ci.error, \
                 x.costs_ci.median, x.costs_ci.error, \
                 x.failure_rate_ci.median, x.failure_rate_ci.error, \
                 x.error_locs_ci.median, int(x.error_locs_ci.error)))

sys.stdout.write("MF histogram...")
sys.stdout.flush()
time_histogram(mf, "mf_histogram.pdf")
print
sys.stdout.write("Error locations histogram...")
sys.stdout.flush()
error_locs_histogram(mf, mfrev, "mf_mfrev_error_locs_histogram_full.pdf")
error_locs_histogram(mf, mfrev, "mf_mfrev_error_locs_histogram_zoomed.pdf", zoom=75)
print
