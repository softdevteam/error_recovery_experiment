# Experiment for "Don't Panic! Better, Fewer, Syntax Errors for LR Parsers"

This is the experiment for the paper ["Don't Panic! Better, Fewer, Syntax
Errors for LR Parsers"](https://arxiv.org/abs/1804.07133) by Lukas Diekmann and
Laurence Tratt. The repository for the paper can be found at
https://github.com/softdevteam/error_recovery_paper.


## Obtaining a corpus

### Using the same corpus we did

You will need to download a fixed release of the experiment from
https://github.com/softdevteam/error_recovery_experiment that contains a
`blackbox/combos` file. This allows you to recreate the corpus we used
of real Java code from [Blackbox](https://bluej.org/blackbox/), part of the
BlueJ editor. For confidentiality reasons, Blackbox data cannot be directly
distributed, but we can distribute the (inherently anonymous) database IDs
which allow you to recreate precisely the corpus we used in the paper. In order
to do this, you need to send an email to the Blackbox developers
`blackbox-admin@bluej.org` requesting access. If/when your request is accepted,
you will be given access to the Blackbox server.

Login to the Blackbox server and execute the following commands:

```
mkdir error_recovery_experiment
cd error_recovery_experiment
wget https://archive.org/download/error_recovery_experiment/0.4/error_recovery_experiment-0.4.tar.gz
tar xfz error_recovery_experiment-0.4.tar.gz
cd blackbox
mkdir src_files
./combos_to_files.py
tar cfz ~/src_files.tgz src_files
```

The `combos_to_files.py` command takes about 9 hours to run, and the `tar`
command a further 30 minutes. This will turn the IDs in `blackbox/combos` into
a compressed tar file of source files located at `~/src_files.tgz`. It is this
latter file (about 80MiB big) which you should then copy to the machine that
you wish to run the main experiment on. Note that this file contains data that
is subject to your agreement with Blackbox (i.e. it must not be distributed to
anyone who was not named in the initial Blackbox request).

Copy the `src_files.tgz` file to the machine you wish to run the main
experiment on. **Please do not run the experiment on the Blackbox server!**


### Generating a new Blackbox corpus

You can generate a new corpus of data from
[Blackbox](https://bluej.org/blackbox/), part of the BlueJ editor. For
confidentiality reasons, Blackbox data cannot be directly distributed, but you
can obtain an agreement to access it yourself. In order to do this, you need to
send an email to the Blackbox developers `blackbox-admin@bluej.org` requesting
access. If/when your request is accepted, you will be given access to the
Blackbox server.

Login to the Blackbox server and execute the following commands:

```
git clone https://github.com/softdevteam/error_recovery_experiment
cd error_recovery_experiment/blackbox
```

You will then need to edit the `gen_combos.py` file at around line 50 to
specify the username and password that the BlueJ developers have given you.

You will then need to install a recent stable version of Rust (e.g. using
[Rustup](https://rustup.rs/)) for your user.

You can then build the blackbox data:

```
./build_blackbox_data.sh
tar cfz ~/src_files.tgz src_files
```

Copy the `src_files.tgz` file to the machine you wish to run the main
experiment on. **Please do not run the experiment on the Blackbox server!**


## Installing dependencies

To run the experiments on your local machine, you need to install LaTeX, Python
2.7, Rust 1.42 (or later). To build the paper you will also need to install Dia
and Inkscape.

In order to process the results (i.e. generate PDF graphs and LaTeX tables),
you will need to install the following Python libraries: matplotlib, pandas,
and seaborn. There are various ways to do this (e.g. OS packages; PIP), so
please use whichever mechanism you are most comfortable with.

There are several ways to install Rust, but [Rustup](https://rustup.rs/)
is generally the easiest, as it installs it solely for your user account:

```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

When asked, select `1) Proceed with installation (default)` to install.


## Running the experiment

When you have installed the dependencies, and assuming you copied
`src_files.tgz` to the root of your home directory, execute the following
commands:

```
git clone https://github.com/softdevteam/error_recovery_experiment
cd error_recovery_experiment/blackbox
tar xfz ~/src_files.tgz
cd ../runner
./build.sh
```

This will download and build the various parser variants used in the experiment
(taking about 10 minutes).

At this point you then need to decide whether you want to run the full
experiment or not. The full experiment takes about 15 days to run and about 10
hours to process the generated data. You can reduce the execution time by
cutting down the number of times that data is rerun / reprocessed: this will
slightly reduce the quality of the subsequent data, although it should not
substantially affect your ability to tell whether you have replicated the
paper's results or not. We suggest changing: the `PEXECS` variable in
`runner/run.py` from 30 to 3; and the `BOOTSTRAP` variable in
`runner/process.py` from 10,000 to 100. With these numbers, the experiment
takes about 11 hours to run and data processing takes about 10 minutes to run.

You should then execute the following commands:

```
./run.sh
./process.py
```

The `run.sh` command produces some rough statistics as it progresses -- these
are simple sanity checks that are not fully post-processed and are not directly
comparable with numbers in the paper. `process.py` produces a number of `.ltx`
and `.pdf` files.  You can examine these individually, or you can rebuild our
paper with the data from your run by first downloading the paper source:

```
git clone https://github.com/softdevteam/error_recovery_paper
cd error_recovery_paper
```

Copy the `.ltx` and `.pdf` files you have created into the root of the
`error_recovery_paper` directory and execute `make` (if on *BSD, you will need
to use `gmake`). This will build a file `error_recovery.pdf` which should be a
version of the paper with your data in.


## A brief guide to the source code

The experiment downloads the
[grmtools](https://github.com/softdevteam/grmtools/) library, checks out a
fixed version of it, and then builds several variants of a Java parser (the
`runner/java_parser_*` executables). It does this by repeatedly patching
grmtools and the Java parser, clearing any existing build, and then rebuilding
the Java parser. `runner/build.sh` shows which patches are used for each
variant.

The source code for the Java parser can be found in `runner/java_parser`: in
essence, it is a thin wrapper around the Java grammar which reports some simple
statistics.

For more information on grmtools itself, the best starting point is the
[grmtools book](https://softdevteam.github.io/grmtools/master/book/) and/or the
API documentation (this is split into sub-libraries, though the [lrpar
API](https://docs.rs/lrpar/0.6.2/lrpar/) is probably the most relevant).

The bulk of the error recovery code itself can be found in
`runner/grmtools/lrpar/src/lib/cpctplus.rs` although some of the helper
functions are in `runner/grmtools/lrpar/src/lib/mf.rs`. Both files are fairly
heavily commented to help you match them up against the paper.
