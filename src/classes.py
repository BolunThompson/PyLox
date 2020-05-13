from __future__ import annotations
import typing
import dataclasses
import collections


@dataclasses.dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: typing.Any
    line: int

    def __str__(self):
        return self.lexeme


class TokenType(collections.UserString):
    def __repr__(self):
        return f"{self.__class__.__name__}({self.data})"

    def __str__(self):
        return repr(self)


class _nil_type:
    """ Should be, and is assumed to be, a singleton """
    def __repr__(self):
        return 'nil'


nil = _nil_type()

lox_literal = typing.Union[bool, float, str, _nil_type]
stmt_literal = typing.Optional[lox_literal]
