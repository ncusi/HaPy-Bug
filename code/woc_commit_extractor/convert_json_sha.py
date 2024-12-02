#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage: %(scriptName) <all_hashes.json> > all_sha.txt

This script converts sha list in json to sha list in text file.
WoC script cmputeDiff works with list sha provided on standard input:
$ echo b15d78fd348c963d5df649a986b31c9b2dd36b43 | ~/lookup/cmputeDiff
$ cat all_sha.txt | ~/lookup/cmputeDiff
"""
import json
import sys


def main():
    all_hashes_filename = sys.argv[1]

    data = json.load(open(all_hashes_filename))
    for sha in data:
        print(sha)


if __name__ == '__main__':
    main()
