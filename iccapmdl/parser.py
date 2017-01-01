from ply.yacc import yacc
from collections import namedtuple
from .listparser import define_list, p_empty
from .lexer import lexer, tokens

Node = namedtuple('Node', ['name', 'mytype', 'value', 'children'])

def p_setup(p):
    "setup : LINK DAT STRING LBRACE setupcontents RBRACE"
    p[0] = Node('Setup', p[3], '', p[5])

def p_applic(p):
    "applic : APPLIC error NEWLINE"
    pass
    #"applic : APPLIC STRING INTEGER INTEGER INTEGER NEWLINE"
def p_subapp(p):
    "subapp : SUBAPP error NEWLINE"
    pass
    #"subapp : SUBAPP STRING INTEGER NEWLINE"
def p_table(p):
    "table : TABLE STRING NEWLINE LBRACE elements RBRACE"
    p[0] = p[5]
    "table : TABLE STRING NEWLINE LBRACE elements RBRACE"

Element = namedtuple('Element', ['index', 'name', 'value'])
def p_element_index(p):
    '''element : ELEMENT INTEGER STRING STRING
               | ELEMENT INTEGER STRING STRING STRING'''
    p[0] = Element(p[2], p[3], p[4])
def p_element_noindex(p):
    '''element : ELEMENT STRING STRING
               | ELEMENT STRING STRING STRING'''
    p[0] = Element(None, p[3], p[4])

p_elements = define_list('elements', ['element'])
p_setupcontents = define_list('setupcontents',
                              ['applic'
                              ,'subapp'
                              ,'table'
                              ,'input'
                              ,'output'
                              ,'transform'
                              ,'plot'
                              ,'data'])

def build(**kwargs):
    return yacc(**kwargs)
