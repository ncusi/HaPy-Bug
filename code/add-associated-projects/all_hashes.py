import json

json_file = '/Users/killer/proj/tssp/python_cve_dataset/associated-projects.json'

with open(json_file) as file:
    json_data = json.load(file)

json_cve_data = list(json_data.values())
projects = [cve['projects'] for cve in json_cve_data]
commits = [project['commits'] for pack in projects for project in pack]
commits = [commit for pack in commits for commit in pack]

print(len(commits))

commits = set(commits)
print(len(commits))
commits = list(commits)

with open('all_hashes.json', 'w') as file:
    json.dump(commits, file)

with open("/Users/killer/proj/tssp/server_diffs.json") as file:
    server_diffs = json.load(file)

server_diffs = set(server_diffs)
commits = set(commits)

diff = commits.difference(server_diffs)

diff = list(diff)
print(len(diff))

with open('read_diffs.json', 'w') as file:
    json.dump(diff, file)
