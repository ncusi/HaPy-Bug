# HaPy-Bug - Human Annotated Python Bug Resolution Dataset
https://2025.msrconf.org/details/msr-2025-data-and-tool-showcase-track/29/HaPy-Bug-Human-Annotated-Python-Bug-Resolution-Dataset

DOI: https://doi.org/10.6084/m9.figshare.24448663

Structure:
* 'annotated_data' and 'collective' contain manual annotations extracted from label studio instance
* 'code' contains scripts used to gather data and prepare dataset
* 'label-studio' contains copy of label studio sources used for manual annotations
* 'label-studio-frontend' contains modified copy of label studio frontend used for manual annotation
* 'raw_data' contains gathered data before manual annotation
* 'Paper.ipynb' contains notebook to open manual annotations and replicate paper experiments

Dataset schema for automated tools is in "code/Documentation/Dataset_structure.md"

Annotations protocol is in "code/Documentation/miniatura_protocol.md"

Annotations schema is as follows:
* 'annotated_data' contains json files extracted from label studio
* prefix letter of name of file denotes annotator, for instance "A_1_24.json" was annotated by annotator "A"
* in file there is a list of annotations, each entry on the list has fields containing 
  * bug description and metadata in "data" field
  * results of annotators actions in "result" field
* Following entries are stored in "result" field as directory 
  * entries with type 'choices' like "annotations-were-problematic", "reviewer-is-sure", "bug-type" contain selected answers
  * entry with type 'cve' contains line and file annotations
    * subentry "diffsFiles" contains "fileName", assigned category "category" and annotated lines in "lines", divided into "afterChange" and "beforeChange" of specific commit

## How to use the dataset:
Write a script to load data from "annotated_data" directory and process it according to your needs.

Example first "data/cve" entry
```
{'id': 'CVE-2019-11340',
 'publicationDate': '19-04-2019',
 'severityScore': '4.3',
 'summary': 'util/emailutils.py in Matrix Sydent before 1.0.2 mishandles registration restrictions that are based on e-mail domain, if the allowed_local_3pids option is enabled. This occurs because of potentially unwanted behavior in Python, in which an email.utils.parseaddr call on user@bad.example.net@good.example.com returns the user@bad.example.net substring.'}
```

Corresponding example first "result" entry taken from "A_1_24.json" file, for manual annotations of 'sydent/util/emailutils.py':
```
[{'value': {'choices': ['application/library']},
  'id': 'g4UOah3mt_',
  'from_name': 'bug-type',
  'to_name': 'text-bug-type',
  'type': 'choices',
  'origin': 'manual'},
 {'value': {'choices': ['yes']},
  'id': 'OhaMoaD2UT',
  'from_name': 'reviewer-is-sure',
  'to_name': 'text-reviewer-is-sure',
  'type': 'choices',
  'origin': 'manual'},
 {'value': {'choices': ['no']},
  'id': '3VdKlaBUh9',
  'from_name': 'annotations-were-problematic',
  'to_name': 'text-annotations-were-problematic',
  'type': 'choices',
  'origin': 'manual'},
 {'type': 'cve',
  'value': {'hyperlinks': [{'url': 'https://matrix.org/blog/2019/04/18/security-update-sydent-1-0-2/',
     'dates': {'min': '2019-04-18', 'max': '2019-04-18'},
     'labels': ['Release Notes', 'Vendor Advisory']},
    {'url': 'https://twitter.com/matrixdotorg/status/1118934335963500545',
     'dates': {'min': None, 'max': None},
     'labels': ['Third Party Advisory']},
    {'url': 'https://github.com/matrix-org/sydent/commit/4e1cfff53429c49c87d5c457a18ed435520044fc',
     'dates': {'min': '2019-04-18', 'max': '2019-04-26'},
     'labels': ['Patch', 'Third Party Advisory']},
    {'url': 'https://github.com/matrix-org/sydent/compare/7c002cd...09278fb',
     'dates': {'min': '2019-04-18', 'max': '2019-04-18'},
     'labels': ['Patch', 'Third Party Advisory']}],
   'diffsFiles': [[{'fileName': 'sydent/util/emailutils.py',
      'category': 'programming',
      'lines': {'afterChange': [{'lineNumber': 58, 'category': 'other'},
        {'lineNumber': 59, 'category': 'bug(fix)'},
        {'lineNumber': 60, 'category': 'bug(fix)'},
        {'lineNumber': 61, 'category': 'bug(fix)'},
        {'lineNumber': 64, 'category': 'refactoring'},
        {'lineNumber': 81, 'category': 'refactoring'},
        {'lineNumber': 82, 'category': 'documentation'},
        {'lineNumber': 83, 'category': 'documentation'},
        {'lineNumber': 84, 'category': 'documentation'},
        {'lineNumber': 85, 'category': 'documentation'},
        {'lineNumber': 86, 'category': 'bug(fix)'}],
       'beforeChange': [{'lineNumber': 58, 'category': 'other'},
        {'lineNumber': 59, 'category': 'bug(fix)'},
        {'lineNumber': 60, 'category': 'bug(fix)'},
        {'lineNumber': 61, 'category': 'bug(fix)'},
        {'lineNumber': 80, 'category': 'bug(fix)'}]}}]]}}]
```

## Data sourced from Github projects:
* 23andMe
* aaugustin
* advisories
* aio-libs
* alex
* andialbrecht
* ansible
* ansible-collections
* aresch
* Backblaze
* bbangert
* bbengfort
* black
* blackducksoftware
* candlepin
* ceph
* cookiecutter
* crossbario
* d0c-s4vage
* django
* dlitz
* dogtagpki
* facebook
* fastapi
* fchollet
* fedora-infra
* Flask-Middleware
* gzpan123
* httpie
* httplib2
* hynek
* IdentityPython
* ipython
* jakubroztocil
* jbarlow83
* jdennis
* jkbrzt
* jpadilla
* jptomo
* kennethreitz
* keras
* keras-team
* kovidgoyal
* Kozea
* latchset
* lericson
* lkiesow
* luigi
* lxml
* marshmallow-code
* martinpitt
* matplotlib
* matrix-org
* MirahezeBots
* mongodb
* Morgan-Phoenix
* mpdavis
* nltk
* numpy
* nvbn
* OpenIDC
* open-iscsi
* openssl
* openstack
* pallets
* pandas
* pandas-dev
* peopledoc
* pikepdf
* pyca
* pygments
* Pylons
* pypa
* py-pdf
* PySnooper
* pytest-dev
* python
* python-babel
* python-discord
* python-pillow
* recurly
* rg3
* rohe
* ros
* rpm-software-management
* samuelcolvin
* sanic
* scottcwang
* scrapy
* sh4nks
* sickcodes
* spacy
* spesmilo
* starkbank
* tadashi-aikawa
* tensorflow
* thanethomson
* thefuck
* theupdateframework
* tiangolo
* tlsfuzzer
* toastdriven
* tomoh1r
* tornado
* tornadoweb
* tqdm
* trevp
* triaxtec
* twisted
* ultrajson
* urllib3
* vyperlang
* yaml
* youtube-dl
* zeromq
* zopefoundation
