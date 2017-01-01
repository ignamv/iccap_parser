import ply.lex

reserved = [
 'LINK'     # major IC-CAP building block
,'applic'   # application window that can be opened by IC-CAP
,'subapp'   # title within an application
,'TABLE'    # collection of user-modifiable elements
,'element'  # user-programmable field (input box)
,'HYPTABLE' # table that is dynamically configured by IC-CAP
,'BLKEDIT'  # block editor text follows (note: leading space in text)
,'CNTABLE'  # connection table-not currently used in IC-CAP
,'PSTABLE'  # parameter set table
,'param'    # model parameter name and value
,'data'     # configuration data follows belonging to the LINK item
,'dataset'  # collection of numerical data
,'datasize' # dimensional information for a dataset
,'type'     # MEASured, SIMUlated, or COMMON data points to follow
,'point'    # individual data value-index, row, column, real value, 
            # imaginary value
,'list'     # this item is dependent on the owning LINK item
,'member'   # the owning LINK item is dependent on this item
,'BOTH'
,'CIRC'
,'COMMON'
,'CONN'
,'DAT'
,'DPS'
,'DUT'
#,'EPL'
#,'GAMMA'
#,'L'
,'MEAS'
,'OPTIMEDIT'
,'OUT'
,'PLOT'
,'PS'
,'SIMU'
,'SWEEP'
,'TCIRC'
,'XFORM'
,'applic'
,'circuitdeck'
,'connpair'
,'editsize'
,'plotsize'
]

t_ignore = ' '

tokens = [
 'INTEGER'
,'FLOAT'
,'STRING'
,'BLOCK'
,'ID'
,'LBRACE'
,'RBRACE'
,'NEWLINE'
] + [r.upper() for r in reserved]

t_LBRACE = '{\n'
t_RBRACE = '}\n'
t_NEWLINE = '\n'
def t_INTEGER(t):
    '[+-]?\d+'
    t.value = int(t.value)
    return t
def t_FLOAT(t):
    '[-+]?(\d+\.?\d*|\d*\.?\d+)([eE][-+]?\d+)?'
    t.value = float(t.value)
    return t
def t_STRING(t):
    '"[^"]*"'
    t.value = t.value[1:-1]
    return t
def t_BLOCK(t):
    '{\n( [^\n]*\n)+}'
    t.value = ''.join(line[1:] for line in t.value[2:-1].split('\n'))
    return t
def t_ID(t):
    '[a-zA-Z]\w*'
    if t.value in reserved:
        t.type = t.value.upper()
    #else:
        #print(t.value)
    return t

def t_error(t):
    raise Exception(t.value)

lexer = ply.lex.lex()
