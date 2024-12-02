import os
import json

json_file = '/mnt/data/CVE/copy/associated-projects.json'
root_folder = '/mnt/data/CVE/copy/data'

with open(json_file) as file:
    json_data = json.load(file)

json_cve_data = list(json_data.values())

directories = [name for name in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, name))]

cves = [cve['cve_id'] for cve in json_cve_data]

cve_set = set(cves)
dir_set = set(directories)

both = cve_set.intersection(dir_set)
# print("Both: ", both)

only_cve = cve_set.difference(dir_set)
# print("Only cve: ", only_cve)

only_dirs = dir_set.difference(cve_set)
# print("Only dirs: ", only_dirs)

cve_diff_data = {'both': list(both), 'only_cve': list(only_cve), 'only_dirs': list(only_dirs)}

# with open('cve_diff_data.json', 'w') as file:
#     json.dump(cve_diff_data, file)

for entry in json_cve_data:
    if entry['cve_id'] in directories:
        cve_folder = os.path.join(root_folder, entry['cve_id'])
        cve_file = os.path.join(cve_folder, 'associated.json')

        with open(cve_file, 'w') as file:
            json.dump(entry['projects'], file)
