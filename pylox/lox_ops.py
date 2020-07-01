from __future__ import annotations

import operator as op
from typing import TYPE_CHECKING, Callable, Dict, Final

import pylox.lox_utils as lu
from pylox.token_classes import TokenType as tt

if TYPE_CHECKING:
    import pylox.lox_types as lt
    import pylox.token_classes as tc

    BinaryLoxOp = Callable[[lt.LoxLiteral, lt.LoxLiteral], lt.LoxLiteral]
    UnaryLoxOp = Callable[[lt.LoxLiteral], lt.LoxLiteral]
    LogicalLoxOp = Callable[[lt.LoxLiteral, lt.LoxLiteral], bool]
    LoxOp = Callable[..., lt.LoxLiteral]


BINARY_FUNCTIONS: Final[Dict[tc.TokenType, BinaryLoxOp]] = {
    tt.MINUS: op.sub,
    tt.SLASH: op.truediv,
    tt.STAR: op.mul,
    tt.PLUS: op.add,
    tt.GREATER: op.gt,
    tt.GREATER_EQUAL: op.ge,
    tt.LESS: op.lt,
    tt.LESS_EQUAL: op.le,
    tt.EQUAL_EQUAL: op.eq,
    tt.BANG_EQUAL: op.ne,
}


UNARY_FUNCTIONS: Final[Dict[tc.TokenType, UnaryLoxOp]] = {
    tt.MINUS: op.neg,
    tt.BANG: lambda x: not lu.lox_true(x),
}
