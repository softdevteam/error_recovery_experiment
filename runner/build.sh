#! /bin/sh

set -e

LRPARV=b7c01b1c
GRAMMARSV=fb1c6550

if [ ! -d lrpar ]; then
    git clone https://github.com/softdevteam/lrpar
    cd lrpar
    git checkout ${LRPARV}
    patch -p0 < ../print_budget.patch
    cargo build --release
    cd ..
fi

if [ ! -d lrpar_rev ]; then
    git clone https://github.com/softdevteam/lrpar lrpar_rev
    cd lrpar_rev
    git checkout ${LRPARV}
    patch -p0 < ../print_budget.patch
    patch -p0 < ../rev_rank.patch
    cargo build --release
    cd ..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout ${GRAMMARSV}
    cd ..
fi

./run.py src_files lrpar/target/release/lrpar cpctplus grammars/java7/java.l grammars/java7/java.y cpctplus.csv
./run.py src_files lrpar/target/release/lrpar cpctplusdyndist grammars/java7/java.l grammars/java7/java.y cpctplusdyndist.csv
./run.py src_files lrpar/target/release/lrpar mf grammars/java7/java.l grammars/java7/java.y mf.csv
./run.py src_files lrpar_rev/target/release/lrpar mf grammars/java7/java.l grammars/java7/java.y mf_rev.csv
