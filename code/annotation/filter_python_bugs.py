import glob
import json
import re
import shutil
from collections import Counter, defaultdict

import click
import pandas as pd
import tqdm


def json_read(fname):
    data = {}
    try:
        f = open(fname, "r")
        data = json.load(f)
    except:
        print("No such file", fname)
        pass
    return data


def explore_path(glob_path):
    structure = defaultdict(Counter)

    for ff in tqdm.tqdm(glob.glob(glob_path + "/**/annotation/*.json"), disable=False):
        cve_name = ff.split("/")[-3]
        data = json_read(ff)

        language = Counter()
        file_type = Counter()
        purpose = Counter()

        for file in data:
            if "language" in data[file]:
                language[("language", data[file]["language"])] += 1
            if "type" in data[file]:
                file_type[("type", data[file]["type"])] += 1
            if "purpose" in data[file]:
                purpose[("purpose", data[file]["purpose"])] += 1

        if ("language", "Python") in language:
            structure[cve_name].update(purpose)
            structure[cve_name].update(language)
            structure[cve_name].update(file_type)

    return structure

def filter_path(glob_path, data):
    for ff in tqdm.tqdm(glob.glob(glob_path + "/**"), disable=False):
        bug_name = ff.split("/")[-1]
        if bug_name not in data:
            shutil.rmtree(ff)

@click.command()
@click.argument("dirs", nargs=-1)
def run(dirs):
    datasets = {}
    for d in dirs:
        datasets[d] = explore_path(d)

    CVE_ID = Counter()
    exclude = []
    data = {}
    for r in datasets:
        data.update(datasets[r])

        for bug in datasets[r]:
            if bug.replace("CRAWL-","") in CVE_ID:
                exclude.append(bug)
            CVE_ID[bug.replace("CRAWL-","")] += 1

    df = pd.DataFrame.from_dict(data, orient='index')
    df = df[~df.index.isin(exclude)]
    df.sort_index(axis=1, inplace=True)

    df.to_excel("dataset.xlsx")
    df.to_parquet('dataset.parquet.gz', compression='gzip')

    for d in dirs:
        filter_path(d, data)

if __name__ == "__main__":
    run()
