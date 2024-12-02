#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: %(scriptName) <all_diffs.txt>

Saves files (blobs) to prepare diff, needs to be run on WoC servers.
Assumes that 'lookup' repository was cloned into home directory:
# git clone https://bitbucket.org/swsc/lookup ~/lookup
Requires result of following script to prepare diffs:
$ cat all_sha.txt | ~/lookup/cmputeDiff > all_diffs.txt
"""
import subprocess
import sys

import pandas as pd


def main():
    diff_summary_filename = sys.argv[1]
    column_names = ['commit', 'file_path', 'file_blob_sha_before', 'file_blob_sha_after']
    df = pd.read_csv(diff_summary_filename, sep=";", encoding='latin-1', names=column_names)
    df['file_blob_sha_before'].apply(save_blob)
    df['file_blob_sha_after'].apply(save_blob)


def save_blob(blob_sha):
    """
    Should run lookup/showCnt blob for provided blob sha
    Example
    subprocess.run("echo bab8a8837dab8b5df135395dfba99dbae6b0a967 | ~/lookup/showCnt blob > bab8a8837dab8b5df135395dfba99dbae6b0a967", shell=True, check=True)
    :param blob_sha: blob to save
    """
    try:
        if blob_sha != '' and type(blob_sha) is str and len(blob_sha) == 40:
            command = "echo " + blob_sha + " | ~/lookup/showCnt blob > " + blob_sha
            print(command)
            subprocess.run(command, shell=True, check=True)
    except:
        print("Cannot retrieve blob", blob_sha)
        pass


if __name__ == '__main__':
    main()
