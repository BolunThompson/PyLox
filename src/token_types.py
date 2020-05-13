import typing
from classes import TokenType


AND = TokenType('AND')

BANG = TokenType('BANG')

BANG_EQUAL = TokenType('BANG_EQUAL')

CLASS = TokenType('CLASS')

COMMA = TokenType('COMMA')

DOT = TokenType('DOT')

ELSE = TokenType('ELSE')

EOF = TokenType('EOF')

EQUAL = TokenType('EQUAL')

EQUAL_EQUAL = TokenType('EQUAL_EQUAL')

FALSE = TokenType('FALSE')

FOR = TokenType('FOR')

FUN = TokenType('FUN')

GREATER = TokenType('GREATER')

GREATER_EQUAL = TokenType('GREATER_EQUAL')

IDENTIFIER = TokenType('IDENTIFIER')

IF = TokenType('IF')

LEFT_BRACE = TokenType('LEFT_BRACE')

LEFT_PAREN = TokenType('LEFT_PAREN')

LESS = TokenType('LESS')

LESS_EQUAL = TokenType('LESS_EQUAL')

MINUS = TokenType('MINUS')

NIL = TokenType('NIL')

NUMBER = TokenType('NUMBER')

OR = TokenType('OR')

PLUS = TokenType('PLUS')

PRINT = TokenType('PRINT')

RETURN = TokenType('RETURN')

RIGHT_BRACE = TokenType('RIGHT_BRACE')

RIGHT_PAREN = TokenType('RIGHT_PAREN')

SEMICOLON = TokenType('SEMICOLON')

SLASH = TokenType('SLASH')

STAR = TokenType('STAR')

STRING = TokenType('STRING')

SUPER = TokenType('SUPER')

THIS = TokenType('THIS')

TRUE = TokenType('TRUE')

VAR = TokenType('VAR')

WHILE = TokenType('WHILE')

EMPTY = TokenType('EMPTY')

RESERVED_WORDS: typing.final = {'and': AND,
                                'class': CLASS,
                                'else': ELSE,
                                'false': FALSE,
                                'for': FOR,
                                'fun': FUN,
                                'if': IF,
                                'nil': NIL,
                                'or': OR,
                                'print': PRINT,
                                'return': RETURN,
                                'super': SUPER,
                                'this': THIS,
                                'true': TRUE,
                                'var': VAR,
                                'while': WHILE}

# Not all statements, just ones with token_types associated with them
STMTS: typing.Final = {PRINT}
