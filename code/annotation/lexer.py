import os
from collections import defaultdict

import pygments
from pygments import lexers, util
from pygments.token import Token


class Lexer(object):
    """Docstring for Lexer."""

    def __init__(self):
        """TODO: to be defined."""
        self.lexers = {}

    def get_lexer(self, filename):
        base, suffix = os.path.splitext(filename)

        if suffix in self.lexers:
            return self.lexers[suffix]

        try:
            lexer = pygments.lexers.get_lexer_for_filename(filename)
        except pygments.util.ClassNotFound:
            lexer = None

        self.lexers[suffix] = lexer

        return lexer

    def lex(self, fname, code):
        lexer = self.get_lexer(fname)

        if not lexer:
            return []

        return list(pygments.lex(code, lexer))
