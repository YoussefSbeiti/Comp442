import ply.lex as lex
import re

class Lexer:
    # List of token names. This is always required
    tokens = [
        'PLUS', 
    'invalidintNum',
    'invalidfloatNum',
    'intNum',
    'floatNum',
    'id', 
    'sr',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'ASSIGN',
    'EQUAL',
    'notEQ',
    'LT',
    'GT',
    'LEQ',
    'GEQ',
    'LCB',
    'RCB',
    'LSB',
    'RSB',
        'BLOCKCOMMENT',
    'INLINECOMMENT',
    'COMMA',
    'SEMICOLON',
    'COLON',
    'DOT',
    'DOUBLECOLON'
    ]

    reserved = {
        'if' : 'if',
        'then' : 'then',
        'else' : 'else',
        'while' : 'while',
        'class' : 'class',
        'integer' : 'integer',
        'float' : 'float',
        'do' : 'do',
        'end': 'end',
        'public' : 'public',
        'private' : 'private',
        'or' : 'or',
        'and' : 'and',
        'not' : 'not',
        'read' : 'read',
        'write' : 'write',
        'return': 'return',
        'main' : 'main',
        'inherits' : 'inherits',
        'local' : 'local',
        'void' : 'void'
    }

    tokens = tokens + list(reserved.values());

    def t_while(self,t): r'while'; return t
    def t_then(self,t): r'then'; return t
    def t_write(self,t): r'write'; return t
    def t_if(self,t): r'if'; return t
    def t_else(self,t): r'else'; return t
    def t_class(self,t): r'class'; return t
    def t_float(self,t): r'float'; return t
    def t_inherits(self,t): r'inherits'; return t
    def t_local(self,t): r'local'; return t
    def t_main(self,t): r'main'; return t
    def t_read(self,t): r'read'; return t
    def t_not(self,t): r'not'; return t
    def t_private(self,t): r'private'; return t
    def t_public(self,t): r'public'; return t
    def t_integer(self,t): r'integer'; return t
    def t_return(self,t): r'return'; return t
    def t_do(self,t): r'do'; return t
    def t_end(self,t): r'end'; return t
    def t_or(self,t): r'or'; return t
    def t_and(self,t): r'and'; return t
    def t_void(self,t): r'void'; return t

    # Regular expression rules for simple tokens
    t_invalidintNum = r'0\d+'
    #t_invalidfloatNum = r'(?:(?:0\d+)\.\d*(?:e-?\d*)?)|(?:(?:[1-9]\d*)\.(?:\d+)e-?(?:0\d*)?)(?!.)'
    t_intNum = r'(?:[1-9]\d*)|(?:0(?!\d+))'
    t_floatNum = r'(?:(?:[1-9]\d*)|0+)\.\d+(?:e-?(?:[1-9]\d*))?'
    t_PLUS    = r'\+'

    
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_id = r'[a-z|A-Z]([a-z|A-Z]|\d|_)*'
    t_BLOCKCOMMENT =r"(?P<blockcomment>/\*(?:\n|[^(\*/)])*\*/)"
    t_INLINECOMMENT = r"(?P<inlineComment>.*//.*\n)"
    #t_floatNum = r'(?:[1-9]\d*|0)+\.(?:[1-9]\d*|0)+'
    t_ASSIGN = r'='
    t_EQUAL = r'=='
    t_LT = r'<'
    t_GT = r'>'
    t_LEQ = r'<='
    t_GEQ = r'>='
    t_notEQ = r'<>'
    t_LCB = r'{'
    t_RCB = r'}'
    t_LSB = r'\['
    t_RSB = r']'
    t_COLON = r':'
    t_SEMICOLON = r';'
    t_DOT = r'\.'
    t_DOUBLECOLON = r'::'
    t_COMMA = r','

    # A regular expression rule with some action code
    def t_invalidfloatNum(self,t):
        r'(?:(?:0\d+)\.\d*(?:e-?\d*)?)|(?:(?:[1-9]\d*)\.(?:\d+)e-?(?:0\d*))'
        return t

      # Build the lexer
    def build(self,**kwargs):
         self.lexer = lex.lex(module=self, **kwargs)

    # Define a rule so we can track line numbers
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self,t):
        printNum("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

