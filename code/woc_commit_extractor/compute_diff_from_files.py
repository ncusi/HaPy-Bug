#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: %(scriptName) <all_diffs.txt>

Computes and saves diffs from saved files (blobs), needs to be run on WoC servers.
Diffs are saved with format "commit_diff"
Example ac36c763c7eb483d0d243423991f13cf9f11d976_diff
for following entry in all_diffs.txt:
"ac36c763c7eb483d0d243423991f13cf9f11d976;/requirements.txt;cdaf8b7b5883f73ecea27b1b385c20c0b4607425;5d37a84ea3d778478cc986c7d1136afc5baaa6dd"
Requires results of following script to compute diffs:
$ retrieve_diff_lines.py all_diffs.txt
"""
import subprocess
import sys

import pandas as pd


def main():
    diff_summary_filename = sys.argv[1]
    column_names = ['commit', 'file_path', 'file_blob_sha_before', 'file_blob_sha_after']
    df = pd.read_csv(diff_summary_filename, sep=";", encoding='latin-1', names=column_names)
    commits_with_files = df.values.tolist()
    for commit_with_files in commits_with_files:
        calculate_diff(commit_with_files)


def calculate_diff(commit_with_files):
    """
    Invokes diff via subprocess and stores results as new file
    :param commit_with_files: list, should contain entry corresponding to change in one file for specific commit
    """
    commit = commit_with_files[0]
    path = commit_with_files[1]
    file_sha_before_change = commit_with_files[2]
    file_sha_after_change = commit_with_files[3]
    if not (isinstance(file_sha_before_change, str)):
        file_sha_before_change = '/dev/null'
    if not (isinstance(file_sha_after_change, str)):
        file_sha_after_change = '/dev/null'
    try:
        command = "diff -u " + file_sha_before_change + " " + file_sha_after_change + " >> " \
                  + commit + "_diff"
        print(command)
        subprocess.run(command, shell=True, check=True)
    except:
        print("Cannot calculate diff", commit, u' '.join(path).encode('utf-8').strip())
        pass


if __name__ == '__main__':
    main()
