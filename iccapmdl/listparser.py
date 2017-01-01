import ply.yacc
import logging

logger = logging.getLogger(__name__)

def p_empty(p):
    'empty : '
    pass

def define_list(name, element_types, separator=''):
    def p_list(p):
        if len(p) == 2:
            p[0] = []
        else:
            p[1].append(p[3 if separator else 2])
            p[0] = p[1]
    p_list.__doc__ = name + ' : empty \n| ' + ' \n| '.join(
        ' '.join([name, separator, type]) for type in element_types)
    logger.debug(p_list.__doc__)
    return p_list

