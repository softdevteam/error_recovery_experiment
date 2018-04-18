# Error recovery experiment

This experiment comes in two phases:

  1. Generate Blackbox data
  2. Run the experiments


## Generate Blackbox data

You will need to ask the BlueJ developers for a Blackbox account. This comes
with various conditions which you must adhere to.

Once you have done that, the scripts in the `blackbox` directory can be used to
generate Java source files from user input. Run `build_blackbox_data.sh` on
the Blackbox server and, many hours later, you will have a `combos` file (which
is the list of pairs needed to regenerate the source files) as well as the
Java source in a `src_files` directory. **The latter must never be
redistributed.** However, the `combos` file is safe to redistribute.


## Run the experiments

`cd runner && ./build.sh` will build the experiments. If files called
`runner/lrpar_Cargo.lock` or `runner/lrpar_rev_Cargo.lock` are present, they
will be used as `Cargo.lock` files for `mf` and `mfref`.

`cd runner && ./run.sh` will run the experiments. You need to have a directory
`src_files` with all the relevant source files *inside* the `runner/` directory.
Output files will be called `runner/*.csv`.

Human friendly PDF and TeX files can be produced with `cd runner &&
./process.py`.
