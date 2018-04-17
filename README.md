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
redistributed.** However, the `combos` file is safe is redistribution.


## Run the experiments

`cd runner && ./build.sh` will build and run the experiments. Output files will
be `runner/*.out`. Output PDF and TeX files can be produced with `cd runner &&
./process.py`.
