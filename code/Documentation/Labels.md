# Dataset glossary - labels

This file describes proposed labels; this would then need to be translated into
a format that Label Studio can use - see [Label Studio Documentation: Labeling
configuration][1].

[1]: https://labelstud.io/guide/setup.html

## Changed files

Different types of automatically generated label for each changed file in the
bugfix commit.

### Programming language

Here the result would be programming language detected by the tool (or list of
languages with probabilities), together with the name of the tool.

List of possible tools:

- GitHub's [Linguist][] library (and data in its [languages.yml][] file)<br>
  with its `--breakdown` mode of `github-linguist` CLI tool
    - [langstat][] is a Python project that uses Linguist's `languages.yml` file
- [Pygments][] can guess lexer name from filename with `pygmentize -N`<br>
  (and with `pygmentize -g` guesses it from the file contents)
- UNIX / Linux [file][] utility (which uses data from `/usr/share/misc/magic`)<br>
  or use [python-magic][] Python's innterface to the `magic` library,<br>
  or use [file-magic][], or [mimetypes][], or pure-Python [filetype][].
  

[Linguist]: https://github.com/github-linguist/linguist
[languages.yml]: https://github.com/github-linguist/linguist/blob/master/lib/linguist/languages.yml
[langstat]: https://github.com/Destaq/langstats
[Pygments]: https://pygments.org/
[file]: https://linux.die.net/man/1/file
[python-magic]: https://github.com/ahupp/python-magic
[filetype]: https://github.com/h2non/filetype.py
[file-magic]: https://pypi.python.org/pypi/file-magic
[mimetypes]: https://docs.python.org/library/mimetypes.html

### Generic file type

This list may need update after examining few CVEs for Python.

- tests
- interface (headers)
- source code
- documentation (for project and for code)
- configuration (including build configuration, dependency configuration, CI setup)
- data
- other


## Changed lines

The list of labels for diff chunks, lines, or ranges of lines (or whole files)
may depend on the file type.

### Line-labels for tests

- description
- comment
- arrange (preparation before test, usually common for a set of tests)
- when (activity being tested, also known as act)
- assert (comparing expected result with actual result)
- other

### Line-labels for source code

This list might need revising.

- docs (this includes docstrings and specially formatted comments for reference documentation)
- comments (automatically generated, assuming whole line is a comment)
- preparation (helping to create a fix)
- fix (fixing a bug)
- futureproofing (making it so the bug is less likely to occur)
- unrelated (not connected to bug fixing)
- other

