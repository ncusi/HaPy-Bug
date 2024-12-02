# Adding associated projects

I need to extract CVEs related to python. For that I will use cve-search api, where title or summary contains regex 'python'.

My goal here is to expand the dataset with data from WoC.  

I will be using [cleaned_cve_df](https://dagshub.com/ncusi/secret_life_of_CVEs/src/main/data/cleaned_cve_df) to get information about all CVEs.  

The result should be a folder with lots of files like `CVE-1234-4321.json` with the following JSON structure

```json
[
    {
        "project": "abc",
        "commits": [
            "0b2f7fd951809e7b37b0d267400bccda101d469c",
            "0b2f7fd951809e7b37b0d267400bccda101d469c"
        ]
    }
]
```

If needed, this should be easily converted to the appropriate folder structure, and commit diffs can be easily acquired from their hashes.
