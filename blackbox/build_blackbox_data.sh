#! /bin/sh

set -e

GRMTOOLSV=9fe6b86b92662a5db44ea33454ccdd3131160a5b
GRAMMARSV=926274486b2e81c78cf41faa6a600e62bd788772

cd ../runner
./build.sh
cd ../blackbox

if [ -d src_files ]; then
    echo "src_files directory must be deleted before running this script." >& 2
    exit 1
fi

if [ ! -d grmtools ]; then
    git clone https://github.com/softdevteam/grmtools
    cd grmtools/lrlex && git checkout ${GRMTOOLSV}
    cargo build --release
    cd ../..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout ${GRAMMARSV}
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
