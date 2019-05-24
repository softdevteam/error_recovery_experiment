# Error recovery experiment

This experiment comes in two phases:

  1. Generate Blackbox data
  2. Run the experiments


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
`blackbox/src_files`.


### Generating fresh data

If you want to generate a fresh batch of Blackbox data (or if you have just
cloned this repository), you will first need to edit `blackbox/gen_combos.py`
and (around line 50) enter the username and password that the BlueJ developers
have given you. On the Blackbox server you should then run the following
commands:

```sh
$ cd blackbox
$ ./build_blackbox_data.sh
```

When that completes, the source files will be placed in `blackbox/src_files`.
Note that this is a slow process taking many hours, most of which is spent
generating a fresh `blackbox/combos` file.


## Run the experiments

`cd runner && ./build.sh` will build the experiments. If
`runner/java_parser/Cargo.lock` is present, it will be used as the `Cargo.lock`
file to build all the parser variants (i.e. recreating the build from our
paper).

In order to run the experiments you need to execute `cd runner && mv
../blackbox/src_files .`. You can then simple execute `./run.sh` in the
`runner` directory. This will create output files named `runner/*.csv`.

Human friendly PDF and TeX files can then be produced by running `./process.py`
in the `runner` directory.
