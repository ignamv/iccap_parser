import unittest
from .. import lexer
import glob
import os

class TestLexer(unittest.TestCase):
    def test_examples(self):
        examples = glob.glob(os.path.join(os.path.dirname(__file__),
                                           'iccapfiles', '*.txt'))
        lexed_dir = os.path.join(os.path.dirname(__file__),
                                 os.pardir, 'lexed')
        if not os.path.exists(lexed_dir): os.mkdir(lexed_dir)

        for example in examples:
            with open(example) as fd:
                content = fd.read()
            with self.subTest(os.path.basename(example)):
                lexer.input(content)
                tokens = list(lexer)
            lexed_filename = os.path.join(lexed_dir, 
                                          os.path.basename(example)+'.txt')
            with open(lexed_filename, 'w') as fd:
                fd.write('\n'.join(map('{0.type!r}\t{0.value!r}'.format, tokens)))
