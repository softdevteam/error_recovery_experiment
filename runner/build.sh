#! /bin/sh

set -e

LRPARV=18921c9b
GRAMMARSV=fb1c6550

if [ ! -d lrpar ]; then
    git clone https://github.com/softdevteam/lrpar
    cd lrpar
    if [ ! -f ../lrpar_Cargo.lock ]; then
        cp ../lrpar_Cargo.lock Cargo.lock
    fi
    git checkout ${LRPARV}
    patch -p1 < ../print_budget.patch
    cargo build --release
    cd ..
fi

if [ ! -d lrpar_rev ]; then
    git clone https://github.com/softdevteam/lrpar lrpar_rev
    cd lrpar_rev
    if [ ! -f ../lrpar_rev_Cargo.lock ]; then
        cp ../lrpar_rev_Cargo.lock Cargo.lock
    fi
    git checkout ${LRPARV}
    patch -p1 < ../print_budget.patch
    patch -p0 < ../rev_rank.patch
    cargo build --release
    cd ..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout ${GRAMMARSV}
    cd ..
fi

if [ ! -d pykalibera ]; then
    git clone https://github.com/softdevteam/libkalibera/
    mv libkalibera/python/pykalibera pykalibera
    rm -rf libkalibera
fi
