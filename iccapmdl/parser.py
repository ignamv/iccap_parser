'''IC-CAP .mdl file parsing routines'''
from collections import namedtuple
import re
from os import SEEK_CUR
import logging
import numpy as np
logger = logging.getLogger(__name__)

__all__ = [
    'parsefile'
]

WORD = re.compile(rb'[^" ]+|"[^"]*"|^\s*$')
LBRACE = (b'{\r\n',)
RBRACE = (b'}\r\n',)
LINK_TYPES = {
    b'MODEL': 'Model',
    b'DUT': 'Dut',
    b'DAT': 'Setup',
    b'SWEEP': 'Input',
    b'OUT': 'Output'
}


MIN_POINT_LENGTH = len('point 0 1 1 0 0\n')
def skippoints(stream, npoints):
    '''Skip a dataset'''
    position = 0
    while npoints - position > 3:
        stream.seek((npoints - position - 1) * MIN_POINT_LENGTH, SEEK_CUR)
        # Discard partial line
        stream.readline()
        # Find current position
        words = WORD.findall(stream.readline())
        if not words[0] == b'point':
            raise Exception(words)
        position = int(words[1]) + 1
    for position in range(position, npoints-1):
        stream.readline()
    line = stream.readline()
    # If I'm not at index (npoints - 1), something went wrong
    if int(WORD.findall(line)[1]) != npoints - 1:
        raise Exception(line)


def readtoken(stream):
    '''Read a token (list of words in a line) from file'''
    return tuple(WORD.findall(stream.readline()))


def tokens(stream):
    '''Yield tokens from file'''
    while True:
        try:
            yield readtoken(stream)
        except StopIteration:
            return


class Node(namedtuple('Node_', ['type_', 'name', 'children', 'vars'])):
    '''Element of .mdl file tree'''
    def __repr__(self, indent=0):
        children = ','.join('\n' + c.__repr__(indent + 1)
                            for c in self.children)
        space = ' ' * indent
        return '{space}Node({!r}, {!r}, [{children}{space}], {!r})'.format(
            self.type_, self.name, self.vars, children=children, space=space)


def skipblock(stream):
    '''Skip lines until brace-delimited block is over'''
    level = 1
    while level > 0:
        line = stream.readline()
        if line.startswith(b'{'):
            level += 1
        elif line.startswith(b'}'):
            level -= 1
        elif not line:
            return
        logger.debug('Skipped line %s', line)


def read_points(stream, npoints):
    '''Read dataset as numpy array'''
    value = np.genfromtxt(stream, delimiter=' ', max_rows=npoints,
                          usecols=(4, 5), unpack=True)
    if (value[:, 1] == 0).all():
        return value[:, 0]
    else:
        return value.view(complex)


def parsefile(stream):
    '''Read Node tree from file'''
    path = [Node(b'Main', b'', [], {})]
    handlers = {}

    def handle(prefix):
        '''Register function as handler for tokens starting with prefix'''
        def wrap(func):
            '''-'''
            handlers[prefix] = func
            return func
        return wrap

    @handle(RBRACE[0])
    def _rbrace():
        '''Add current node to children of the previous node in path'''
        previous = path.pop()
        parent = path[-1]
        if previous.type_ == b'':
            # Collapse contents of empty Node (from DATA token) to parent
            parent.children.extend(previous.children)
            parent.vars.update(previous.vars)
        else:
            parent.children.append(previous)

    @handle(b'LINK')
    def _link(type_, name, *dummy):
        '''Add empty node to path'''
        name = name[1:-1]
        type_ = LINK_TYPES.get(type_, type_)
        path.append(Node(type_, name, [], {}))
        assert readtoken(stream) == LBRACE

    @handle(b'data\r\n')
    def _data():
        '''Translate data to empty Node'''
        path.append(Node(b'', b'', [], {}))
        assert readtoken(stream) == LBRACE

    @handle(b'TABLE')
    def _dut_model_vars(tabletype, *dummy):
        '''Read dut/model vars into last Node in path'''
        if tabletype != b'"Variable Table"':
            return
        assert readtoken(stream) == LBRACE
        while True:
            token = readtoken(stream)
            assert token[0] == b'element'
            name = token[3][1:-1]
            token = readtoken(stream)
            assert token[0] == b'element'
            value = token[3][1:-1]
            if not name and not value:
                assert readtoken(stream) == RBRACE
                break
            path[-1].vars[name] = value

    @handle(b'HYPTABLE')
    def _tablevars(*dummy):
        '''Read TableVars into last Node in path'''
        assert readtoken(stream) == LBRACE
        while True:
            token = readtoken(stream)
            if token == RBRACE:
                break
            assert token[0] == b'element'
            path[-1].vars[token[1][1:-1]] = token[2][1:-1]

    @handle(b'dataset\r\n')
    def _dataset():
        '''Read dataset into vars MEAS or SIMU of last node in path'''
        assert readtoken(stream) == LBRACE
        token = readtoken(stream)
        assert token[0] == b'datasize'
        npoints = int(token[2])
        while True:
            token = readtoken(stream)
            if token[0].startswith(b'}'):
                break
            assert token[0] == b'type'
            dset = read_points(stream, npoints)
            path[-1].vars[token[1]] = dset
            logger.debug('Dataset at %s shape %s dtype %s', stream.tell(),
                         dset.shape, dset.dtype)

    @handle(LBRACE[0])
    def _lbrace():
        '''This wasn't read by other handlers so skip the block'''
        logger.debug('Skip from %s at %s', token[0], stream.tell())
        skipblock(stream)
        logger.debug('Skip to %s', stream.tell())

    @handle(b'element')
    @handle(b'point')
    def _mishandled(*token):
        '''Should have been skipped by other handler, raise exception'''
        raise Exception(*token)

    
    @handle(b'')
    def _eof(*_token):
        raise StopIteration()

    while True:
        token = readtoken(stream)
        try:
            handlers[token[0]](*token[1:])
        except KeyError:
            logger.debug('Skip token %s', token[0])
        except StopIteration:
            return path[0]
