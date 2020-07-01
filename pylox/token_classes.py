from __future__ import annotations

import enum
import typing as tp
from dataclasses import dataclass

if tp.TYPE_CHECKING:
    import pylox.lox_types as lt


class TokenType(str, enum.Enum):
    AND = "AND"
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    CLASS = "CLASS"
    COMMA = "COMMA"
    DOT = "DOT"
    ELSE = "ELSE"
    EOF = "EOF"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    FALSE = "FALSE"
    FOR = "FOR"
    FUN = "FUN"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAl"
    IDENTIFIER = "IDENTIFIER"
    IF = "IF"
    LEFT_BRACE = "LEFT_BRACE"
    LEFT_PAREN = "LEFT_PAREN"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    MINUS = "MINUS"
    NIL = "NIL"
    NUMBER = "NUMBER"
    OR = "OR"
    PLUS = "PLUS"
    PRINT = "PRINT"
    RETURN = "RETURN"
    RIGHT_BRACE = "RIGHT_BRACE"
    RIGHT_PAREN = "RIGHT_PAREN"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    STAR = "STAR"
    STRING = "STRING"
    SUPER = "SUPER"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"
    EMPTY = "EMPTY"
    BREAK = "BREAK"


# TODO: Get around dataclass, __slots__ issue?
@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: tp.Optional[lt.LoxLiteral]
    line: int

    def __str__(self) -> str:
        return self.lexeme


TokenSeq = tp.Sequence[Token]
sentinel_token = Token(TokenType.EMPTY, "", None, 0)
