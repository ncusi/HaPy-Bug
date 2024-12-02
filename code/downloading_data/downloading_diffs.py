import urllib
import requests
import github
from github import Github
import json
import os

import validators

g = Github("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")


def isUrl(v):
    return isinstance(v, str) and validators.url(v)


def findUrls(d):
    """Returns a set of urls occurring in a dictionary."""
    urls = set()
    if isinstance(d, dict):
        for k, v in d.items():
            urls.update(findUrls(v))
    elif isinstance(d, list):
        for i in d:
            urls.update(findUrls(i))
    elif isUrl(d):
        urls.add(d)

    return urls


def saveStringToFile(filepath, filename, text, encoding=None):
    """Saves a string to file with the specified path, name and encoding.
    Creates directories if they don't exist."""
    os.makedirs(filepath, exist_ok=True)
    with open(os.path.join(filepath, filename), "w", encoding=encoding) as f:
        f.write(text)


def saveDiffsByUrl(url, filepath):
    """If url is a link to pull request or commit in public GitHub or BitBucket repository,
    saves its diff and patch to files in the specified directory."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.split("/")

    if len(path) < 4:
        return None

    repo_name = path[1] + "/" + path[2]

    if "github" in parsed.netloc:

        if path[3] == "pull":
            repo = g.get_repo(repo_name)
            pull_id = path[4]
            pull = repo.get_pull(int(pull_id))

            # Save diff
            response = requests.get(pull.diff_url)
            diff = response.text
            saveStringToFile(filepath, str(pull_id) + ".diff", diff, response.encoding)

            # Save patch
            response = requests.get(pull.patch_url)
            patch = response.text
            saveStringToFile(filepath, str(pull_id) + ".patch", patch, response.encoding)

        elif path[3] == "commit":
            repo = g.get_repo(repo_name)
            commit_id = path[4]
            commit = repo.get_commit(commit_id)

            diff_url = commit.html_url + ".diff"
            patch_url = commit.html_url + ".patch"

            # Save diff
            response = requests.get(diff_url)
            diff = response.text
            saveStringToFile(filepath, str(commit_id) + ".diff", diff, response.encoding)

            # Save patch
            response = requests.get(patch_url)
            patch = response.text
            saveStringToFile(filepath, str(commit_id) + ".patch", patch, response.encoding)

    elif "bitbucket" in parsed.netloc:
        endpoint = "https://api.bitbucket.org/2.0/repositories/"

        if path[3] == "pull-requests":
            pull_id = path[4]
            pull_url = endpoint + repo_name + "/pullrequests/" + pull_id

            try:
                response = requests.get(pull_url).json()

                # Save diff
                diff_url = response['links']['diff']['href']
                response = requests.get(diff_url)
                diff = response.text
                saveStringToFile(filepath, str(pull_id) + ".diff", diff, response.encoding)

                # Save patch
                diff_url_parsed = urllib.parse.urlparse(diff_url)
                diff_url_path = diff_url_parsed.path.split("/")
                diff_url_path[5] = "patch"
                patch_url = "https://api.bitbucket.org" + "/".join(diff_url_path)
                response = requests.get(patch_url)
                patch = response.text
                saveStringToFile(filepath, str(pull_id) + ".patch", patch, response.encoding)
            except requests.exceptions.JSONDecodeError as e:
                print(e)
                raise e

        elif path[3] == "commits":
            commit_id = path[4]
            commit_url = endpoint + repo_name + "/commit/" + commit_id

            try:
                response = requests.get(commit_url).json()

                # Save diff
                diff_url = response['links']['diff']['href']
                response = requests.get(diff_url)
                diff = response.text
                saveStringToFile(filepath, str(commit_id) + ".diff", diff, response.encoding)

                # Save patch
                patch_url = endpoint + repo_name + "/patch/" + commit_id
                response = requests.get(patch_url)
                patch = response.text
                saveStringToFile(filepath, str(commit_id) + ".patch", patch, response.encoding)
            except (requests.exceptions.JSONDecodeError, KeyError) as e:
                print(e)
                raise e


def saveCommitMessagesByUrl(url, filepath):
    """If url is a link to pull request or commit in public GitHub or BitBucket repository,
    saves its description or messages to files in the specified directory."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.split("/")

    if len(path) < 4:
        return None

    repo_name = path[1] + "/" + path[2]

    if "github" in parsed.netloc:

        if path[3] == "pull":
            repo = g.get_repo(repo_name)
            pull_id = path[4]
            pull = repo.get_pull(int(pull_id))

            saveStringToFile(filepath, str(pull_id) + ".desc", pull.title)

            commits = pull.get_commits()
            for c in commits:
                saveStringToFile(filepath, str(c.sha) + ".message", c.commit.message)

        elif path[3] == "commit":
            repo = g.get_repo(repo_name)
            commit_id = path[4]
            commit = repo.get_commit(commit_id)

            saveStringToFile(filepath, str(commit_id) + ".message", commit.commit.message)

    elif "bitbucket" in parsed.netloc:
        endpoint = "https://api.bitbucket.org/2.0/repositories/"

        if path[3] == "pull-requests":
            pull_id = path[4]
            pull_url = endpoint + repo_name + "/pullrequests/" + pull_id

            try:
                response = requests.get(pull_url).json()

                desc = response['description']
                saveStringToFile(filepath, str(pull_id) + ".desc", desc)

            except (requests.exceptions.JSONDecodeError, KeyError) as e:
                print(e)
                raise e

        elif path[3] == "commits":
            commit_id = path[4]
            commit_url = endpoint + repo_name + "/commit/" + commit_id

            try:
                response = requests.get(commit_url).json()

                message = response['message']
                saveStringToFile(filepath, str(commit_id) + ".message", message)

            except (requests.exceptions.JSONDecodeError, KeyError) as e:
                print(e)
                raise e


# Reads cve_ids from a cves_ids.txt file and calls saveDiffsByUrl for each url in CVE json.
# Saves processed ids and ids where the function raised an exception to processed_cves.txt and errors.txt
# Breaks after nearing GitHub rate limit.

if __name__ == '__main__':
    with open("cve_ids.txt") as file:
        cve_ids = [line.rstrip() for line in file]

    processed = open("processed_cves.txt", 'a')
    errors = open("errors.txt", 'a')

    i = 0
    for cve_id in cve_ids:
        processed.write(cve_id + "\n")
        i += 1

        cve = json.load(open("data/" + cve_id + "/" + cve_id + ".json"))
        urls = findUrls(cve)
        for url in urls:
            try:
                saveDiffsByUrl(url, os.path.join("data", cve_id, "patches"))
            except (github.GithubException, requests.exceptions.JSONDecodeError, KeyError):
                errors.write(cve_id + " " + url + "\n")

        if i % 100 == 0:
            print(i)
            print(g.get_rate_limit())

        remaining, limit = g.rate_limiting
        if remaining < len(urls):
            break

    processed.close()
    errors.close()
