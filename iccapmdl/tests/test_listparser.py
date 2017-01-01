import collections
import unittest
import logging
from iccapmdl.listparser import p_empty, define_list
from iccapmdl.parsercls import Parser

logging.basicConfig(level=logging.DEBUG)

from functional import compose
p_empty = compose(staticmethod, p_empty)
define_list = compose(staticmethod, define_list)

Token = collections.namedtuple('Token', ['type','value']) #,'lineno','lexpos'])

class MockLexer(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
    def token(self):
        try:
            return next(self.iterator)
        except StopIteration:
            return None

class TestListParser(unittest.TestCase):
    def setUp(self):
        class NoSeparatorNumbersParser(Parser):
            def __init__(self):
                self.tokens = ['number']
                self.build(start='numbers')
            p_numbers = define_list('numbers', ['number', 'letter'])
            p_empty = p_empty
            def p_error(self, p):
                raise Exception(p)
        self.parser = NoSeparatorNumbersParser()

    def _parsetokens(self, tokens):
        lexer = MockLexer(tokens)
        return self.parser.parse(lexer=lexer)

    def test_empty(self):
        self.assertEqual([], self._parsetokens([]))
    def test_single(self):
        self.assertEqual([1], self._parsetokens([
            Token('number', 1)]))
    def test_many(self):
        self.assertEqual([1, 5, 8], self._parsetokens([
             Token('number', 1)
            ,Token('number', 5)
            ,Token('number', 8)
        ]))

class TestListParser(unittest.TestCase):
    def setUp(self):
        class NoSeparatorCharsParser(Parser):
            def __init__(self):
                self.tokens = ['number', 'letter']
                self.build(start='characters')
            p_characters = define_list('characters', ['number', 'letter'])
            p_empty = p_empty
            def p_error(self, p):
                raise Exception(p)
        self.parser = NoSeparatorCharsParser()

    def _parsetokens(self, tokens):
        lexer = MockLexer(tokens)
        return self.parser.parse(lexer=lexer)

    def test_empty(self):
        self.assertEqual([], self._parsetokens([]))
    def test_single(self):
        self.assertEqual([1], self._parsetokens([
            Token('number', 1)]))
    def test_many(self):
        self.assertEqual([1, 'a', 8], self._parsetokens([
             Token('number', 1)
            ,Token('letter', 'a')
            ,Token('number', 8)
        ]))
