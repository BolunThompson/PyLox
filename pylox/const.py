from __future__ import annotations

from typing import Dict, Final, Literal, Set, Union
import pylox.lox_types as lt
import pylox.token_classes as tc
from pylox.token_classes import TokenType as tt
import pylox.lox_class as lc
import pylox.functions as fn
import pylox.lox_builtins as lb

# TODO: Consider moving some of these to other files


PY_LOX_STR_TYPES: Final[Dict[Union[lt.NilType, type], str]] = {
    lt.nil: "nil",
    lt.NilType: "nil",
    float: "number",
    int: "number",
    str: "string",
    bool: "boolean",
    lc.LoxInstance: "instance",
    fn.LoxFunction: "function",
    lb.LoxNativeFunction: "native function",
}


StrTokenDict = Dict[str, tc.TokenType]

VALUE_WORDS: Final[Dict[str, Union[Literal[True, False], lt.NilType]]] = {
    "true": True,
    "false": False,
    "nil": lt.nil,
}


RESERVED_WORDS: Final[StrTokenDict] = {
    "and": tt.AND,
    "class": tt.CLASS,
    "else": tt.ELSE,
    "false": tt.FALSE,
    "for": tt.FOR,
    "fun": tt.FUN,
    "if": tt.IF,
    "nil": tt.NIL,
    "or": tt.OR,
    "print": tt.PRINT,
    "return": tt.RETURN,
    "super": tt.SUPER,
    "true": tt.TRUE,
    "var": tt.VAR,
    "while": tt.WHILE,
    "break": tt.BREAK,
}


STR_TOKENS: Final[StrTokenDict] = {
    **RESERVED_WORDS,
    "(": tt.LEFT_PAREN,
    ")": tt.RIGHT_PAREN,
    "{": tt.LEFT_BRACE,
    "}": tt.RIGHT_BRACE,
    ",": tt.COMMA,
    ".": tt.DOT,
    "-": tt.MINUS,
    "+": tt.PLUS,
    ";": tt.SEMICOLON,
    "*": tt.STAR,
    "!": tt.BANG,
    "=": tt.EQUAL,
    "<": tt.LESS,
    ">": tt.GREATER,
    "!=": tt.BANG_EQUAL,
    "==": tt.EQUAL_EQUAL,
    "<=": tt.LESS_EQUAL,
    ">=": tt.GREATER_EQUAL,
    "/": tt.SLASH,
    " ": tt.EMPTY,
    "\r": tt.EMPTY,
    "\t": tt.EMPTY,
    "//": tt.EMPTY,
    "": tt.EMPTY,
    "\n": tt.EMPTY,
    "/*": tt.EMPTY,
    "\\*": tt.EMPTY,
}

SYNC_TOKENS: Final[Set[tc.TokenType]] = {
    tt.CLASS,
    tt.FUN,
    tt.VAR,
    tt.FOR,
    tt.IF,
    tt.WHILE,
    tt.PRINT,
    tt.RETURN,
}
