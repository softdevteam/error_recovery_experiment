# Error recovery experiment

This experiment comes in two phases:

  1. Install dependencies
  2. Generate Blackbox data
  3. Run the experiments


## Install dependencies

To run the experiments you need to install Python 2.7 and Rust. There are
several ways to install Rust, but [rustup](https://rustup.rs/) is generally
the easiest, as it installs it solely for your user account:

```sh
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

When asked, select `1) Proceed with installation (default)` to install Rust.

If you wish to also process the results (i.e. generate PDF graphs and LaTeX
tables), you will need to install LaTeX and the following Python libraries:
matplotlib, pandas, and seaborn. You may optionally use PyPy to process the
results, using [wheels](https://github.com/antocuni/pypy-wheels) to install the
matplotlib, pandas, and seaborn.


## Generate Blackbox data

You will need to ask the BlueJ developers for a Blackbox account. This comes
with various conditions which you must adhere to. The basic process is that you
need to either generate a fresh, or use an existing, `blackbox/combos` file.
From that, Java source files will be written to `blackbox/src_files`. **The
latter must not be redistributed under any circumstances.** However, the
`blackbox/combos` file is safe to redistribute.


### Using the same data we did in the paper

If you are using a formal release of this project (i.e. you have not just
cloned the repository but have downloaded a version which includes a
`blackbox/combos` file), then you can recreate exactly the same Java source
files we used via the following commands:

```sh
$ cd blackbox
$ ./build_blackbox_data.sh
```

This will detect the existing `blackbox/combos` file and use that to recreate
the same Java source files we used: those source files will be put into
`blackbox/src_files`. This process takes around 20 minutes.


### Generating fresh data

If you want to generate a fresh batch of Blackbox data (or if you have just
cloned this repository), you will first need to edit `blackbox/gen_combos.py`
and (around line 50) enter the username and password that the BlueJ developers
have given you. On the Blackbox server you should install Rust (see the
instructions above) and then run the following commands:

```sh
$ cd blackbox
$ ./build_blackbox_data.sh
```

When that completes, the source files will be placed in `blackbox/src_files`.
Note that this is a slow process taking approximately 16-24 hours.


## Run the experiments

Please do not run the experiments on the Blackbox server. Clone this repository
afresh on your experiment machine, and copy the `blackbox/src_files` directory
from the Blackbox server into the `blackbox` directory on your experiment
machine.

The main experiments are in the `runner` directory. In order that you can more
precisely control the environment that these are run in, they are split into
three steps which you should run in the following order:

```sh
$ cd runner
$ ./build.sh # Build the experiments
$ ./run.sh # Run the experiments
$ ./process.py # Generate stats and figures from the experiment data
```

If you installed PyPy, you should change that last line to `pypy process.py`.
Note that, on the full dataset, PyPy takes about 6 hours, whereas CPython takes
about 12 hours, both consuming up to 30GiB RAM at their peak.
