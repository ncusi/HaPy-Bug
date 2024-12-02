# Augmented Python CVE dataset storage format structure

This document describes the format in which the data of the extended CVE dataset
(augmented CVE dataset) will be stored.

Among the data we want to store are:

- data from CVE system, augmented with data from other databases like NVD
- information extracted from references (hyperlinks) in CVE,
  such as dates and categories, both automatically extracted with a script,
  and added / supplemented / verified manually
- information extracted from bugfix commit, including
   - categorization of changed files
   - format of changed files (programming language, or type of document)
   - change analysis (per-file, per-chunk, per-line)
- additional information from other sources

Among other things, we want to store downloaded pages and downloaded bugfix
commits (mainly diff files of changes), for later further analysis (like
sentiment analysis with [VADER][], or extracting topics with LDA or GPT).

[VADER]: https://github.com/cjhutto/vaderSentiment "Valence Aware Dictionary and sEntiment Reasoner"

## Hierarchical structure

We have chosen to store data as multiple separate files, gathered in a
hierarchical structure. This choice was used because it has the advantage that
it makes it easy to write in parallel from multiple processes running on a
compute cluster.

The following directory structure is proposed:

- `data/`
    - `README.md` describing the dataset and its structure
    - `CVE-<id>/` - one per CVE
        - manifest.json, or MANIFEST, or similar file - to be added later
        - `CVE-<id>.json` with data extracted from CVE, CVE-Search, or NVD (raw)<br>
          possibly in [CVE JSON 5.0][CVE_JSON_5] format
        - `references/`, with contents of referenced web pages
            - one file per reference, in `*.html` or `*.txt` formats
        - `patches/`, with raw contents of bugfix commits as patches
            - one file per relevant reference, that is one per bugfix commit<br>
              `<SHA-1 id, or Message-ID, or other name>.patch`
              (or `*.diff` if `*.patch` is not available)
        - `generated/`, with data files in JSON format, generated automatically
        - `label-studio/`, with data file or files in [Label Studio JSON][LS-JSON] format<br>
          można je [generować programistycznie][LS-ML]
    
[CVE_JSON_5]: https://github.com/CVEProject/cve-schema/blob/master/schema/v5.0/CVE_JSON_5.0_schema.json
[LS-JSON]: https://labelstud.io/guide/predictions.html "Import pre-annotated data into Label Studio"
[LS-ML]: https://labelstud.io/guide/ml.html "Integrate Label Studio into your machine learning pipeline"
