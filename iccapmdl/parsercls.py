from ply.yacc import yacc

class Parser(object):
    def build(self, **kwargs):
        self.parser = yacc(module=self, **kwargs)
    def parse(self, *args, **kwargs):
        return self.parser.parse(*args, **kwargs)
