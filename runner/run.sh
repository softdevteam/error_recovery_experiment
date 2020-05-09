#! /bin/sh

set -e

echo "===> cpctplus"
./run.py ../blackbox/src_files ./java_parser_cpctplus 0.5 cpctplus.csv
echo "===> cpctplus_dont_merge"
./run.py ../blackbox/src_files ./java_parser_cpctplus_dontmerge 0.5 cpctplus_dontmerge.csv
echo "===> cpctplus_rev"
./run.py ../blackbox/src_files ./java_parser_cpctplus_rev 0.5 cpctplus_rev.csv
echo "===> cpctplus_long"
./run.py ../blackbox/src_files ./java_parser_cpctplus_longer 2.0 cpctplus_longer.csv
echo "===> corchuelo"
./run.py ../blackbox/src_files ./java_parser_corchuelo 0.5 corchuelo.csv
echo "===> panic"
./run.py ../blackbox/src_files ./java_parser_panic 0.5 panic.csv
