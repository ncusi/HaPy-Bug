import os
import subprocess

import pandas as pd
import re

classed_commits = '~/proj/tssp/python_cve_dataset/crawl-dataset/classified'
repo_data = '~/proj/tssp/python_cve_dataset/crawl-dataset/repo_list'
dataset_dir = '/data/MSR/crawl-dataset'

pd.set_option('display.max_columns', None)

classed_commits = pd.read_parquet(classed_commits)
repo_data = pd.read_parquet(repo_data)

cve_commits = classed_commits[classed_commits['CVE'] == True]
cve_commits = cve_commits.dropna(subset=['message'])

g = 0

for i, row in cve_commits.iterrows():
    if g == 5:
        break
    g += 1
    message = row['message']

    pattern = r"CVE-\d{4}-\d{4,7}"
    cve_numbers = re.findall(pattern, message)

    for cve_id in cve_numbers:
        commit = row['commit']

        repo_name = row['repo_name']

        repo_path_df = repo_data[repo_data['repo_name'] == repo_name]
        repo_path_s = repo_path_df['path']
        repo_path = repo_path_s.iloc[0].replace("/data-local", "/data")

        output_path = os.path.join(dataset_dir, f'CRAWL-{cve_id}', 'patches')

        command = ["mkdir", "-p", output_path]
        subprocess.run(command)

        output_message = os.path.join(output_path, f'{commit}.message')
        command = ["git", "show", "-s", commit]
        message_p = subprocess.run(command, cwd=repo_path, stdout=subprocess.PIPE)
        try:
            output_text = message_p.stdout.decode()
        except UnicodeDecodeError as e:
            continue
        with open(output_message, "w") as output_file:
            output_file.write(output_text)

        output_diff = os.path.join(output_path, f'{commit}.diff')
        command = ["git", "diff", "-p", f'{commit}^', commit]
        diff_p = subprocess.run(command, cwd=repo_path, stdout=subprocess.PIPE)
        try:
            output_text = diff_p.stdout.decode()
        except UnicodeDecodeError as e:
            continue
        with open(output_diff, "w") as output_file:
            output_file.write(output_text)
