import json

import pygments
from pygments.token import Token
from pygments import lexers
from pygments import util
from collections import defaultdict
import os
import glob

import asyncio


def tokenizeCodeInDiff(diff_lines):
    """Parameter is a diff in the form of list of strings, where each string is another line of diff output
    (along with newline characters at the end of each line)
     Returns a dictionary with following items:
     - diff: input parameter joined into a single string with newline characters
     - lexer: a dictionary. Keys are line numbers. Values are lists of tuples (a, b).
              a - lexeme occurring in the respective line, b - token type assigned by Pygments lexer
     - files: list of filenames from diff
     - filestolines: a dictionary.
                     Keys are filenames, values are line numbers where the diff heading with the respective file occurs in the diff output
     - possible_wrong_numbering: list of tuples (a, b).
                                 a - position of change for which there's a difference between number of newlines found by diff lexer and code lexer
                                 b - the difference between those numbers
  """
    # Find lines where another file starts
    headings_indices = [i for i, line in enumerate(diff_lines) if line.startswith("diff")]
    headings_indices.append(len(diff_lines))

    diff_lines_by_file = []  # lists of lists of diff output lines, every list is a different file
    for previous, current in zip(headings_indices, headings_indices[1:]):
        diff_lines_by_file.append(diff_lines[previous:current])

    code_lines_with_numbers = defaultdict(list)
    files = []
    files_to_lines = dict()
    mismatches = []

    for file_diff, h_index in zip(diff_lines_by_file, headings_indices):  # iterate over files listed in diff
        # Find lines where another change starts
        subheadings_indices = [i for i, line in enumerate(file_diff) if line.startswith("@@")]
        subheadings_indices.append(len(file_diff))

        # Find lexer for the file
        filename = file_diff[0].split(" ")[2]
        if filename == "/dev/null":
            filename = file_diff[0].split(" ")[3]
        files.append(filename)
        try:
            lexer = pygments.lexers.get_lexer_for_filename(filename)
        except pygments.util.ClassNotFound:
            lexer = None

        changes_in_file = []  # lists of lists of diff output lines
        # every list is a different change made in the current file
        for previous, current in zip(subheadings_indices, subheadings_indices[1:]):
            changes_in_file.append(file_diff[previous:current])

        for change, subh_index in zip(changes_in_file, subheadings_indices):  # iterate over changes made in file
            # skip first line which is a diff subheading
            # and skip first char of each line
            code_lines = [line[1:] for line in change[1:]]

            # if first or last line is just a newline character, lexer ignores it, which breaks numbering
            if code_lines[0] == "\n":
                code_lines[0] = " \n"
            if code_lines[-1] == "\n":
                code_lines[-1] = " \n"

            code = ''.join(code_lines)
            if lexer:
                code_tokens = list(pygments.lex(code, lexer))
            else:
                code_tokens = list(pygments.lex(code, pygments.lexers.guess_lexer(code)))
            diff_tokens = list(pygments.lex(''.join(change[1:]), pygments.lexers.DiffLexer()))

            # code_tokens = [(t[0], t[1].rstrip(" ")) for t in code_tokens]

            # Assign tokens to line numbers
            position = h_index + subh_index + 2  # line number in diff where the change starts
            i = 0
            for t in code_tokens:
                code_lines_with_numbers[i + position].append(t)
                if (t[0] == Token.Text.Whitespace or t[0] == Token.Comment.Preproc) and t[1].isspace():
                    i += len(t[1].split("\n")) - 1
                elif t[0] == Token.Comment.Multiline or issubclass(t[0].__class__, Token.Literal.String.__class__):
                    i += len(t[1].split("\n")) - 1

            line_count = diff_tokens.count((Token.Text.Whitespace, '\n'))
            if i != line_count:  # if different, line numbering might be inaccurate
                mismatches.append((position, line_count - i))

        files_to_lines[filename] = h_index + 1

    output = {
        "diff": "".join(diff_lines) + "\n",
        "lexer": code_lines_with_numbers,
        "files": files,
        "filestolines": files_to_lines,
        "possible_wrong_numbering": mismatches
    }
    return output


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


@background
def saveTokenized(cve_id, path="."):
    """Calls tokenizeCodeInDiff for each .diff file in path/data/cve_id/patches/,
     where cve_id and path are function arguments. Saves output to json files in path/data/cve_id/generated/
     Creates one file in processed/ directory for each processed cve.
     Creates one file in errors/ directory for each cve where tokenizeCodeInDiff or saving to file raised an exception.
     The point of this is to be able to track the progress."""
    filenames = glob.glob("*.diff", root_dir=os.path.join(path, cve_id, "patches"))
    for filename in filenames:
        with open(os.path.join(path, cve_id, "patches", filename)) as f:
            lines = [line for line in f]

        os.makedirs(os.path.join(path, cve_id, "generated"), exist_ok=True)
        with open(os.path.join(path, cve_id, "generated", filename + ".json"), 'w') as f:
            try:
                output = tokenizeCodeInDiff(lines)
                json.dump(output, f)
            except Exception as e:
                print(cve_id, e)
                # os.makedirs("errors/", exist_ok=True)
                # with open("errors/" + cve_id, 'a') as errors:  # create file for every failed cve
                #     errors.write(cve_id + "\n")

    # with open("processed/" + cve_id, 'w') as processed:  # create file for every processed cve
    #     processed.write(cve_id + "\n")


if __name__ == '__main__':
    # file with all names of folder to work on
    dirs_file = ''

    # path to dataset to work on
    dataset = ''

    with open(dirs_file) as f:
        cves = [line.rstrip() for line in f]

    loop = asyncio.get_event_loop()

    looper = asyncio.gather(*[saveTokenized(cve_id, dataset) for cve_id in cves])

    results = loop.run_until_complete(looper)

    print("done")
