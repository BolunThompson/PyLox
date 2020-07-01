from pylox.lox_types import nil
from pylox.token_classes import Token, TokenType


#TODO: Use mocking?

_source_text = (
    "2+2;\n"
    " /* 𐀀 ⍅*/ // \r\n"
    "\tif (nil) {var x = 3/2; print x+-2.1;} fun test(a, b) {;}\n"
    "true==false\n"
    '"test"=="test"'
)

SOURCE = (
    _source_text,
    (
        Token(type=TokenType("NUMBER"), lexeme="2", literal=2.0, line=1),
        Token(type=TokenType("PLUS"), lexeme="+", literal=None, line=1),
        Token(type=TokenType("NUMBER"), lexeme="2", literal=2.0, line=1),
        Token(type=TokenType("SEMICOLON"), lexeme=";", literal=None, line=1),
        Token(type=TokenType("IF"), lexeme="if", literal=None, line=2),
        Token(type=TokenType("LEFT_PAREN"), lexeme="(", literal=None, line=2),
        Token(type=TokenType("NIL"), lexeme="nil", literal=nil, line=2),
        Token(type=TokenType("RIGHT_PAREN"), lexeme=")", literal=None, line=2),
        Token(type=TokenType("LEFT_BRACE"), lexeme="{", literal=None, line=2),
        Token(type=TokenType("VAR"), lexeme="var", literal=None, line=2),
        Token(type=TokenType("IDENTIFIER"), lexeme="x", literal=None, line=2),
        Token(type=TokenType("EQUAL"), lexeme="=", literal=None, line=2),
        Token(type=TokenType("NUMBER"), lexeme="3", literal=3.0, line=2),
        Token(type=TokenType("SLASH"), lexeme="/", literal=None, line=2),
        Token(type=TokenType("NUMBER"), lexeme="2", literal=2.0, line=2),
        Token(type=TokenType("SEMICOLON"), lexeme=";", literal=None, line=2),
        Token(type=TokenType("PRINT"), lexeme="print", literal=None, line=2),
        Token(type=TokenType("IDENTIFIER"), lexeme="x", literal=None, line=2),
        Token(type=TokenType("PLUS"), lexeme="+", literal=None, line=2),
        Token(type=TokenType("MINUS"), lexeme="-", literal=None, line=2),
        Token(type=TokenType("NUMBER"), lexeme="2.1", literal=2.1, line=2),
        Token(type=TokenType("SEMICOLON"), lexeme=";", literal=None, line=2),
        Token(type=TokenType("RIGHT_BRACE"), lexeme="}", literal=None, line=2),
        Token(type=TokenType("FUN"), lexeme="fun", literal=None, line=2),
        Token(type=TokenType("IDENTIFIER"), lexeme="test", literal=None, line=2),
        Token(type=TokenType("LEFT_PAREN"), lexeme="(", literal=None, line=2),
        Token(type=TokenType("IDENTIFIER"), lexeme="a", literal=None, line=2),
        Token(type=TokenType("COMMA"), lexeme=",", literal=None, line=2),
        Token(type=TokenType("IDENTIFIER"), lexeme="b", literal=None, line=2),
        Token(type=TokenType("RIGHT_PAREN"), lexeme=")", literal=None, line=2),
        Token(type=TokenType("LEFT_BRACE"), lexeme="{", literal=None, line=2),
        Token(type=TokenType("SEMICOLON"), lexeme=";", literal=None, line=2),
        Token(type=TokenType("RIGHT_BRACE"), lexeme="}", literal=None, line=2),
        Token(type=TokenType("TRUE"), lexeme="true", literal=True, line=3),
        Token(type=TokenType("EQUAL_EQUAL"), lexeme="==", literal=None, line=3),
        Token(type=TokenType("FALSE"), lexeme="false", literal=False, line=3),
        Token(type=TokenType("STRING"), lexeme='"test"', literal="test", line=4),
        Token(type=TokenType("EQUAL_EQUAL"), lexeme="==", literal=None, line=4),
        Token(type=TokenType("STRING"), lexeme='"test"', literal="test", line=4),
    ),
)


EXPRS = ()
