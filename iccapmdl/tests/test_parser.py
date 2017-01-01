import unittest
import logging
from .. import parser
from ply.yacc import yacc

logging.basicConfig(level=logging.DEBUG)

class TestParserBase(unittest.TestCase):
    def __init__(self, *args, start=None, **kwargs):
        super(TestParserBase, self).__init__(*args, **kwargs)
        self.start = start

    def setUp(self):
        self.parser = yacc(module=parser, start=self.start)

class TestSetupParser(TestParserBase):
    def __init__(self, *args, **kwargs):
        super(TestSetupParser, self).__init__(*args, start='setup', **kwargs)

    def test_stuff(self):
        input_ = self.parser.parse('''\
LINK SWEEP "vh"
{
applic "Display Data" 0 135 489
subapp "Edit Sweep Info" 1
subapp "Display Data" 1
data
{
editsize 10 42
HYPTABLE "Edit Sweep Info"
{
element "Mode" "V"
element "Sweep Type" "LIN"
}
HYPTABLE "Edit Sweep Mode Def"
{
element "+ Node" "H"
element "- Node" "L"
element "Unit" "CM"
element "Compliance" " 1.000 "
}
HYPTABLE "Edit Sweep Def"
{
element "Sweep Order" "1"
element "Start" " 0.000 "
element "Stop" " 5.000 "
element "# of Points" "11"
element "Step Size" " 500.0m"
}
}
list PLOT "clcvsv"
}
''')
        print(input_)
