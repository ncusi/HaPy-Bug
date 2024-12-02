# How to use tokenization, labeling and changes labling scripts

First you need to have a list of all directories in folder you want to work in.
I just did a quick python script like
this

```python
import os

for thing in os.listdir("put dataset dir here"):
    print(thing)
```

and then forwarded output of this to file, later this file is used as dirs_file.

There are 2 variables you need to change in each script so it works for you.
One of them is this `dirs_file` which is what you get after that script.

And then you need to change `dataset` so it is a path to folder where cves or bugs are located.

Then you just run [tokenization.py](../tokenization/tokenization.py),
[file_labeling.py](../categorization/file_labeling.py) and
[changes_labeling.py](../categorization/changes_labeling.py) in this order,
because they depend on each other(or at least file labeling on tokenization)
