import urllib

import pandas as pd
import json


def get_cve_df(length=1000) -> pd.DataFrame:
    """
    Fetches CVEs related to python using CVE search api. The payload, headers and url are taken
    from actual request site made when querying search with regex 'python'. You may change the
    number of max CVEs with length parameter.

    Returns dataframe containing all fetched CVEs
    """
    import requests

    url = "http://158.75.112.151:5000/fetch_cve_data"

    payload = "draw=6&columns%5B0%5D%5Bdata%5D=blank&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=false" \
              "&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D" \
              "%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=id&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D" \
              "=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D" \
              "%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=cvss&columns%5B2%5D%5Bname%5D=&columns%5B2%5D" \
              "%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D" \
              "=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=cvss3&columns%5B3%5D%5Bname%5D" \
              "=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D" \
              "%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=summary&columns%5B4" \
              "%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D" \
              "%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=last" \
              "-modified&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D" \
              "=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6" \
              "%5D%5Bdata%5D=Published&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D" \
              "%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D" \
              f"=false&order%5B0%5D%5Bcolumn%5D=5&order%5B0%5D%5Bdir%5D=desc&start=0&length={length}&search%5Bvalue%5D" \
              "=python&search%5Bregex%5D=true&retrieve=cves"

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,uk-UA;q=0.6,uk;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    df = pd.DataFrame(response.json()['data'])

    return df


def strip_clean_cve(file) -> pd.DataFrame:
    """
    This deletes unneeded data from clean_cve from daskhub, leaving only commit, project names and cve ids
    """
    df = pd.read_parquet(file)
    columns_to_keep = ["commit", "project_names", "commit_cves"]
    df = df[columns_to_keep]
    df.rename(columns={'commit_cves': 'cve_id', 'project_names': 'project'}, inplace=True)

    return df


def group_dfs(python_cves_df, woc_cves_df):
    """
    Groups and filters world of code CVEs into dataframe, with groupings.
    """
    filtered_woc_cves_df = woc_cves_df[woc_cves_df['cve_id'].isin(python_cves_df['cve_id'])]
    grouped_df = filtered_woc_cves_df.groupby(['cve_id', 'project']).agg({'commit': list}).reset_index()

    grouped_projects_df = grouped_df.groupby('cve_id').apply(lambda x: {'cve_id': x['cve_id'].iloc[0],
                                                                        'projects': [{'project': p, 'commits': c} for
                                                                                     p, c in zip(x['project'], x[
                                                                                'commit'])]}).reset_index(drop=True)

    return grouped_projects_df


print("getting pytohn cves")
python_cves_df = get_cve_df()
print("reading woc cves")
woc_cves_df = strip_clean_cve('/mnt/data/CVE/secret_life_of_CVEs/cleaned_cve_df')
print("Grouping")
python_cves_df.rename(columns={'id': 'cve_id'}, inplace=True)
grouped_dfs = group_dfs(python_cves_df, woc_cves_df)
grouped_dfs.to_json('associated-projects.json')
print("done")
