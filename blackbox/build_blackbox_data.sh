#! /bin/sh

set -e

if [ -d src_files ]; then
    echo "src_files directory must be deleted before running this script." >& 2
    exit 1
fi

if [ ! -d lrlex ]; then
    git clone https://github.com/softdevteam/lrlex
    cd lrlex && git checkout e14e2d4e
    cargo build --release
    cd ..
fi

if [ ! -d lrpar ]; then
    git clone https://github.com/softdevteam/lrpar
    cd lrpar && git checkout 1e533a34
    cargo build --release
    cd ..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout fb1c6550
    cd ..
fi

if [ -f combos ]; then
    echo "===> Using existing combos file"
else
    echo "===> Generating combos file"
    ./gen_combos.py
fi

mkdir src_files
echo "===> Generating src_files"
./combos_to_files.py
