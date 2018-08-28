#! /bin/sh

set -e

./run.py src_files java_parser_cpctplus cpctplus.csv
./run.py src_files java_parser_mf mf.csv
./run.py src_files java_parser_mf_rev mf_rev.csv
./run.py src_files java_parser_panic panic.csv
