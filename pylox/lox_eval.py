from __future__ import annotations

import typing as tp

import pylox.lox_ops as lo
import pylox.lox_utils as lu

if tp.TYPE_CHECKING:
    import pylox.lox_types as lt
    import pylox.token_classes as tc


def evaluate_lox_binary(
    lox_type: tc.TokenType, left: lt.LoxLiteral, right: lt.LoxLiteral
) -> lt.LoxLiteral:
    # new_exc is set to allow the exception to leave the exception
    # handling code to be raised from at the end.
    new_exc: Exception
    try:
        return lo.BINARY_FUNCTIONS[lox_type](left, right)
    except KeyError:
        text = f"The operator {lox_type} is not a binary operator"
    except TypeError:
        if isinstance(left, float) and left == int(left):
            return evaluate_lox_binary(lox_type, int(left), right)
        if isinstance(right, float) and right == int(right):
            return evaluate_lox_binary(lox_type, left, int(right))
        text = (
            f"The operator {lox_type} does not support lox types"
            f" {lu.lox_type(left)} and {lu.lox_type(right)}"
        )
    raise TypeError(text)


def evaluate_lox_unary(lox_type: tc.TokenType, left: lt.LoxLiteral) -> lt.LoxLiteral:
    # new_exc is set to allow the exception to leave the exception
    # handling code to be raised from at the end.
    new_exc: Exception
    try:
        return lo.UNARY_FUNCTIONS[lox_type](left)
    except KeyError as exc:
        text = f"The operator {lox_type} is not a unary operator"
        new_exc = exc
    except TypeError as exc:
        text = f"The operator {lox_type} does not support lox type {lu.lox_type(left)}"
        new_exc = exc
    raise TypeError(text) from new_exc
