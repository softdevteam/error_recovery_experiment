#! /bin/sh

set -e

echo "===> cpctplus"
./run.py src_files java_parser_cpctplus cpctplus.csv
echo "===> mf"
./run.py src_files java_parser_mf mf.csv
echo "===> mf_rev"
./run.py src_files java_parser_mf_rev mf_rev.csv
echo "===> panic"
./run.py src_files java_parser_panic panic.csv
