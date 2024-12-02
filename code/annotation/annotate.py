import codecs
import glob
import json
import os
from collections import defaultdict

import click
import yaml
from joblib import Parallel, delayed
from unidiff import PatchSet
import tqdm

from languages import Languages
from lexer import Lexer

LANGUAGES = Languages()
LEXER = Lexer()

from pygments.token import Token


class AnnotateLine(object):

    """Docstring for AnnotateLine."""

    def __init__(self, patch_file, line):
        """TODO: Docstring for __init__.

        :patch: TODO
        :file: TODO
        :line: TODO
        :returns: TODO

        """
        self.patch_file = patch_file
        self.line = line

    def is_comment(self, tokens_list):
        tl = tokens_list
        prerequisite = False

        result = False
        condition = True

        for t in tl:
            token_type = t[0]
            if t[0] in Token.Comment:
                result = True
            elif t[0] in Token.Text and t[1].isspace():
                # white space in line is also ok
                pass
            else:
                # other tokens
                condition = False

        # Debug
        # if result and not condition:
        #     print(self.line.value, end="")

        if result and condition:
            return True
        return False

    def get(self):
        line = self.line

        # Check if line was changed
        if not ((line.source_line_no is None) ^ (line.target_line_no is None)):
            return None, {}

        if line.source_line_no:
            line_no = line.source_line_no
            fout = self.patch_file.fsource
        else:
            line_no = line.target_line_no
            fout = self.patch_file.ftarget

        purpose = self.patch_file.patch[fout]["purpose"]

        ret = {"id": line_no, "type": purpose}

        if self.patch_file.patch[fout]["type"] != "programming":
            if purpose not in ["documentation", "test"]:
                ret["type"] = "bug(fix)"
        else:
            # For programming languages
            tokens_list = LEXER.lex(fout, line.value)

            if self.is_comment(tokens_list):
                ret["type"] = "documentation"
            elif purpose == "test":
                ret["type"] = "test"
            else:
                ret["type"] = "bug(fix)"

        return fout, ret


class PatchFile(object):

    """Docstring for PatchFile."""

    def __init__(self, file):
        """TODO: to be defined."""

        self.patch = defaultdict(dict)

        self.file = file

        self.fsource = file.source_file
        self.ftarget = file.target_file

        # get the names and drop "a/" and "b/"
        if self.fsource[:2] == "a/":
            self.fsource = file.source_file[2:]
        if self.ftarget[:2] == "b/":
            self.ftarget = file.target_file[2:]

        source_meta_dict = LANGUAGES.annotate(self.fsource)
        self.patch[self.fsource].update(source_meta_dict)

        if self.fsource != self.ftarget:
            target_meta_dict = LANGUAGES.annotate(self.ftarget)
            self.patch[self.ftarget].update(target_meta_dict)

        # Force each file to have changes list -- even if empty changes
        for lt in ["+", "-"]:
            self.patch[self.fsource][lt] = list()
            self.patch[self.ftarget][lt] = list()

    def process(self):
        for hunk in self.file:
            # print(hunk)
            for line in hunk:
                fout, processed_line = AnnotateLine(self, line).get()

                if fout:
                    ltype = line.line_type
                    self.patch[fout][ltype].append(processed_line)

        return self.patch


class Bug(object):

    """Represents single bug in dataset"""

    def __init__(self, dataset, bug):
        """Constructor for class representing single Bug

        :dataset: path to the dataset
        :bug: bug id

        """
        self._dataset = dataset
        self._bug = bug
        self._path = os.path.join(self._dataset, self._bug, "patches")

        self.patches = self._get_patches()
        self.changes = []

    def _get_patch(self, patch_file):
        fname = os.path.join(self._path, patch_file)

        patch = {}

        # Skip diffs between multiple versions
        if "..." in fname:
            return {}

        with codecs.open(fname, "r", encoding="utf-8") as diff:
            try:
                patch_set = PatchSet(diff)
                for file in patch_set:
                    patch_file = PatchFile(file)
                    patch.update(patch_file.process())
            except Exception as e:
                print("Error", patch_file, e)
                # raise e
        return patch

    def save(self, fname, patch):
        base_path = os.path.join(self._dataset, self._bug, "annotation")

        os.makedirs(base_path, exist_ok=True)

        fname = fname.split(".")[0] + ".json"
        out_path = os.path.join(base_path, fname)

        if patch:
            with open(out_path, "w") as f:
                json.dump(patch, f)


    def _get_patches(self):
        "Gathers patches filenames"

        patch_files = glob.glob("*.diff", root_dir=self._path)

        for patch_file in patch_files:
            annotation = self._get_patch(patch_file)

            self.save(patch_file, annotation)


class Bugs(object):

    """Bugs dataset class"""

    def __init__(self, path):
        """Constructor of bug dataset.

        :path: path to the dataset

        """
        self._path = path

        try:
            self.bugs = [d.rstrip() for d in os.listdir(self._path)]
        except Exception as e:
            print("error in Bugs exiting", e)

    def get_bug(self, bug):
        """Return specified bug

        :bug: TODO
        :returns: TODO

        """
        return Bug(self._path, bug)

    def __iter__(self):
        "Iterate over bugs in dataset"
        return self.bugs.__iter__()


def process_bug():
    filenames = glob.glob("*.diff", root_dir=os.path.join(path, cve_id, "patches"))


@click.command()
@click.argument("datasets", nargs=-1)
def run(datasets):
    for dataset in datasets:
        print(f"Dataset {dataset}")
        bugs = Bugs(dataset)
        for bug in tqdm.tqdm(bugs):
            bugs.get_bug(bug)


if __name__ == "__main__":
    run()
