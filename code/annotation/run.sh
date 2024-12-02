#!/usr/bin/env bash
#
# WARNING: this will remove non python projects !

# expected list of directories containing datasets
# example ./run.sh /mnt/data/CVE/final/*

# annotate dataset
python3 annotate.py $@

# reduce number of projects - first run 
python3 filter_python_bugs.py $@

# run to find duplicate patches 
bash find_patch_duplicates.sh $@

# run to fix duplicate diffs and bug reports
python3 remove_duplicates.py bug_duplicates

# final run of filtering to get excel and parquet files
python3 filter_python_bugs.py $@
