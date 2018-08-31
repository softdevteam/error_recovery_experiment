#! /bin/sh

set -e

cd ../runner
./build.sh
cd ../blackbox

if [ -d src_files ]; then
    echo "src_files directory must be deleted before running this script." >& 2
    exit 1
fi

if [ ! -d grmtools ]; then
    git clone https://github.com/softdevteam/grmtools
    cd grmtools/lrlex && git checkout 0b770e02
    cargo build --release
    cd ../..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout 4f42d1a8
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
