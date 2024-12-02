import os
import re
import subprocess

# Where are repositories from bugs in py located
repos_path = '~/proj/tssp/bugs-in-py-dataset'

# Where is bugs in py projects folder
bugs_path = '~/proj/tssp/BugsInPy/projects'

# Where to put resulting dataset
dataset_path = '~/proj/tssp/bugs-dataset'

for project in os.listdir(bugs_path):
    bugs = os.path.join(bugs_path, project, 'bugs')

    for bug_id in os.listdir(bugs):
        bug_id_path = os.path.join(bugs, bug_id)
        if os.path.isdir(bug_id_path):
            bug_info = os.path.join(bug_id_path, 'bug.info')
            with open(bug_info, 'r') as file:
                info_file = file.read()
                fixed_commit_id = re.search(r'fixed_commit_id\s*=\s*"([^"]+)"', info_file).group(1)

                git_repo = os.path.join(repos_path, project)

                output_path = os.path.join(dataset_path, f'{project}-{bug_id}', 'patches')

                command = ["mkdir", "-p", output_path]
                subprocess.run(command)

                output_message = os.path.join(output_path, f'{fixed_commit_id}.message')
                command = ["git", "show", "-s", fixed_commit_id]
                message_p = subprocess.run(command, cwd=git_repo, stdout=subprocess.PIPE)
                output_text = message_p.stdout.decode()
                with open(output_message, "w") as output_file:
                    output_file.write(output_text)

                output_diff = os.path.join(output_path, f'{fixed_commit_id}.diff')
                command = ["git", "diff", "-p", f'{fixed_commit_id}^', fixed_commit_id]
                diff_p = subprocess.run(command, cwd=git_repo, stdout=subprocess.PIPE)
                output_text = diff_p.stdout.decode()
                with open(output_diff, "w") as output_file:
                    output_file.write(output_text)
