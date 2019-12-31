#! /bin/sh

set -e

echo "===> cpctplus"
./run.py ../blackbox/src_files java_parser_cpctplus cpctplus.csv
echo "===> cpctplus_rev"
./run.py ../blackbox/src_files java_parser_cpctplus_rev cpctplus_rev.csv
echo "===> panic"
./run.py ../blackbox/src_files java_parser_panic panic.csv
