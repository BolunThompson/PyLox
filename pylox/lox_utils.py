from __future__ import annotations

import functools
import typing as tp

import pylox.lox_errors as le
import pylox.lox_types as lt
import pylox.token_classes as tc
from pylox import const, results


def token_str_dec(wrapped: tp.Callable) -> tp.Callable:
    @functools.wraps(wrapped)
    def wrapper(
        tokens: tp.Union[tp.Iterable[tp.Union[str, tc.Token]], tp.Union[str, tc.Token]],
        *args: tp.Any,
        **kwargs: tp.Any,
    ) -> tp.Callable:
        token_p_str = ""
        if isinstance(tokens, (str, tc.Token)):
            tokens = (tokens,)
        for token in tokens:
            token_p_str += token.lexeme if isinstance(token, tc.Token) else token
        return wrapped(token_p_str, *args, **kwargs)

    return wrapper


@token_str_dec
def is_lox_number(literal: str) -> bool:
    literal = literal.replace(".", "", 1).replace("e+", "", 1)
    return literal == "" or literal.isdigit()


@token_str_dec
def is_lox_string(literal: str) -> bool:
    return literal[0] + literal[-1] == '""'


@token_str_dec
def is_lox_identifier(literal: str) -> bool:
    return not const.RESERVED_WORDS.get(literal) and (
        literal[0].isalpha() or literal[0] == "_"
    )


def lox_true(value: lt.LoxLiteral) -> bool:
    return value not in {False, lt.nil}


def lox_type(value: lt.LoxLiteral) -> str:
    """ Returns the lox type of the literal. Considers ints a number lox type"""
    try:
        return const.PY_LOX_STR_TYPES[type(value)]
    except KeyError:
        raise TypeError("Value is not lox literal") from None


def lox_str(value: lt.StmtLiteral, *, repl: bool = False) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    if isinstance(value, str):
        if repl:
            value = f'"{value}"'
        return value
    if isinstance(value, float):
        int_value = int(value)
        if int_value == value:
            value = int_value
        return f"{value}"
    return f"{value}"


def lox_print(
    *args: tp.Union[lt.StmtLiteral, results.ResultNT, le.ErrorReturns],
    repl: bool = False,
) -> None:
    for printable in args:
        if isinstance(printable, results.ResultNT):
            printable, error = printable
        elif isinstance(printable, le.ErrorReturns):
            error, printable = printable, None
        else:
            error = le.ErrorReturns.SUCCESS
        if printable is not None and not error.error():
            print(lox_str(printable, repl=repl))
