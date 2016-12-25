'''IC-CAP .mdl file parsing routines'''
from collections import namedtuple
import re
import numpy as np
import sys
from os import SEEK_CUR
import logging
logger = logging.getLogger(__name__)

WORD = re.compile(rb'[^" ]+|"[^"]*"|^\s*$')


def lextoken(line):
    '''Create token (list of words) from line'''
    return WORD.findall(line)


def skippoints(fd, npoints):
    '''Skip a dataset'''
    position = 0
    while npoints - position > 3:
        # Each point line is at least 16 bytes
        fd.seek((npoints - position - 1) * 16, SEEK_CUR)
        # Discard partial line
        fd.readline()
        # Find current poisition
        words = WORD.findall(fd.readline())
        if not words[0] == b'point':
            raise Exception(words)
        position = int(words[1]) + 1
    for position in range(position, npoints-1):
        fd.readline()
    line = fd.readline()
    if int(WORD.findall(line)[1]) != npoints - 1:
        raise Exception(line)


def lexfile(fd):
    for line in fd:
        tok = lextoken(line)
        if tok[0] == b'datasize':
            npoints = int(tok[2])
            fd.readline()
            skippoints(fd, npoints)
            if tok[1] == 'BOTH':
                fd.readline()
                skippoints(fd, npoints)


def readtoken(fd):
    line = fd.readline()
    if not line:
        raise Exception()
    return WORD.findall(line)


class Node(namedtuple('Node_', ['type_', 'name', 'children', 'vars'])):
    def __repr__(self, indent=0):
        children = ',\n'.join(c.__repr__(indent + 1) for c in self.children)
        space = ' ' * indent
        return '{space}Node({!r}, {!r}, [\n{children}{space}], {!r})'.format(
            self.type_, self.name, self.vars, children=children, space=space)


def skipblock(fd):
    level = 1
    while level > 0:
        line = fd.readline()
        if line.startswith(b'{'):
            level += 1
        elif line.startswith(b'}'):
            level -= 1
        elif not line:
            return
        logger.debug('Skipped line %s', line)


def read_points(fd, npoints):
    real, imag = np.genfromtxt(fd, delimiter=' ', max_rows=npoints,
                               usecols=(4, 5), unpack=True)
    if (imag == 0).all():
        return real
    else:
        return real + 1j * imag


def parsefile(fd):
    path = [Node(b'Main', b'', [], {})]
    lbrace = [b'{\r\n']
    rbrace = [b'}\r\n']
    while True:
        try:
            tok = readtoken(fd)
        except:
            return path[0]
        if tok[0].startswith(b'}'):
            previous = path.pop()
            path[-1].children.append(previous)
            continue
        elif tok[0] == b'LINK':
            type_ = tok[1]
            name = tok[2][1:-1]
            path.append(Node(type_, name, [], {}))
            assert readtoken(fd) == lbrace
        elif tok[0] == b'data\r\n':
            path.append(Node(b'', b'', [], {}))
            assert readtoken(fd) == lbrace
        elif tok[0] == b'TABLE' and tok[1] == b'"Variable Table"':
            assert readtoken(fd) == lbrace
            while True:
                tok = readtoken(fd)
                assert tok[0] == b'element'
                name = tok[3][1:-1]
                tok = readtoken(fd)
                assert tok[0] == b'element'
                value = tok[3][1:-1]
                if not name and not value:
                    assert readtoken(fd) == rbrace
                    break
                path[-1].vars[name] = value
        elif tok[0] == b'HYPTABLE':
            assert readtoken(fd) == lbrace
            while True:
                tok = readtoken(fd)
                if tok == rbrace:
                    break
                assert tok[0] == b'element'
                path[-1].vars[tok[1][1:-1]] = tok[2][1:-1]
        elif tok[0] == b'dataset\r\n':
            assert readtoken(fd) == lbrace
            tok = readtoken(fd)
            assert tok[0] == b'datasize'
            npoints = int(tok[2])
            while True:
                tok = readtoken(fd)
                if tok[0].startswith(b'}'):
                    break
                assert tok[0] == b'type'
                dset = read_points(fd, npoints)
                path[-1].vars[tok[1]] = dset
                logger.debug('Dataset at %s shape %s dtype %s', fd.tell(),
                             dset.shape, dset.dtype)
        elif tok[0] == b'point':
            raise Exception(tok)
        elif tok[0].startswith(b'{'):
            logger.debug('Skip from %s at %s', tok[0], fd.tell())
            skipblock(fd)
            logger.debug('Skip to %s', fd.tell())
        else:
            logger.debug('Skip token %s', tok[0])


filename = '/home/ignamv/programacion/iccap/examples/model_files/mosfet/'\
           'bsim4/examples/bsim4_binned/bsim4_binned~data.mdl'
for ii in range(10):
    with open(filename, 'rb') as fd:
        lexfile(fd)
#      1 View
#     37 CNTABLE
#     38 circuitdeck
#     38 PSTABLE
#    244 dataset
#    244 datasize
#    244 type
#    246 TABLE
#    824 data
#    862 LINK
#   1769 HYPTABLE
#   4058 {
#   4058 }
#  12177 element
# 537584 point
