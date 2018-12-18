#! /bin/sh

set -e

GRMTOOLSV=f7ca1425
GRAMMARSV=0660c131

if [ ! -d grmtools ]; then
    git clone https://github.com/softdevteam/grmtools
    cd grmtools
    git checkout ${GRMTOOLSV}
    cd ..
fi

if [ ! -d grammars ]; then
    git clone https://github.com/softdevteam/grammars/
    cd grammars && git checkout ${GRAMMARSV}
    cd ..
    cp grammars/java7/java.l java_parser/src/java7.l
    cp grammars/java7/java.y java_parser/src/java7.y
fi

if [ ! -f java_parser_cpctplus ]; then
    cd grmtools
    git reset --hard
    patch -p0 < ../print_budget.patch
    cd ../java_parser
    sed -Ei "s/RecoveryKind::[a-zA-Z_]*[)]/RecoveryKind::CPCTPlus)/" build.rs
    rm -rf target
    cargo build --release
    cp target/release/java_parser ../java_parser_cpctplus
    cd ..
fi

if [ ! -f java_parser_mf ]; then
    cd grmtools
    git reset --hard
    patch -p0 < ../print_budget.patch
    cd ../java_parser
    sed -Ei "s/RecoveryKind::[a-zA-Z_]*[)]/RecoveryKind::MF)/" build.rs
    rm -rf target
    cargo build --release
    cp target/release/java_parser ../java_parser_mf
    cd ..
fi

if [ ! -f java_parser_mf_rev ]; then
    cd grmtools
    git reset --hard
    patch -p0 < ../print_budget.patch
    patch -p0 < ../rev_rank.patch
    cd ../java_parser
    sed -Ei "s/RecoveryKind::[a-zA-Z_]*[)]/RecoveryKind::MF)/" build.rs
    rm -rf target
    cargo build --release
    cp target/release/java_parser ../java_parser_mf_rev
    cd ..
fi

if [ ! -f java_parser_none ]; then
    cd grmtools
    git reset --hard
    cd ../java_parser
    sed -Ei "s/RecoveryKind::[a-zA-Z_]*[)]/RecoveryKind::None)/" build.rs
    rm -rf target
    cargo build --release
    cp target/release/java_parser ../java_parser_none
    cd ..
fi

if [ ! -f java_parser_panic ]; then
    cd grmtools
    git reset --hard
    patch -p0 < ../print_budget.patch
    cd ../java_parser
    sed -Ei "s/RecoveryKind::[a-zA-Z_]*[)]/RecoveryKind::Panic)/" build.rs
    rm -rf target
    cargo build --release
    cp target/release/java_parser ../java_parser_panic
    cd ..
fi

if [ ! -d pykalibera ]; then
    git clone https://github.com/softdevteam/libkalibera/
    mv libkalibera/python/pykalibera pykalibera
    rm -rf libkalibera
fi
