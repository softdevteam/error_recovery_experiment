#! /bin/sh

set -e

./run.py src_files lrpar/target/release/lrpar cpctplus grammars/java7/java.l grammars/java7/java.y cpctplus.csv
./run.py src_files lrpar/target/release/lrpar mf grammars/java7/java.l grammars/java7/java.y mf.csv
./run.py src_files lrpar_rev/target/release/lrpar mf grammars/java7/java.l grammars/java7/java.y mf_rev.csv
