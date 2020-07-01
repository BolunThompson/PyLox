from __future__ import annotations

import functools
import typing as tp

import pylox.error_dec as ed
import pylox.lox_errors as le
import pylox.lox_utils as lu
import pylox.token_classes as tc
from pylox import const
from pylox.token_classes import TokenType as tt

if tp.TYPE_CHECKING:
    import pylox.lox_types as lt

error = functools.partial(le.error, error_type=le.ErrorReturns.SCAN_ERROR)


def to_token_type(string: str, line: int) -> tp.Optional[tc.TokenType]:
    try:
        return const.STR_TOKENS[string]
    except KeyError:
        pass
    if lu.is_lox_number(string):
        return tt.NUMBER
    if lu.is_lox_string(string):
        return tt.STRING
    if lu.is_lox_identifier(string):
        return tt.IDENTIFIER
    error(line, f"Unexpected Character {string}")
    return None


# TODO: Refactor.


@ed.lox_error_handling(le.ErrorReturns.SCAN_ERROR)
def scan(source: str,) -> tp.Union[tp.List[tc.Token], le.ErrorReturns]:
    current = 0
    line = 1
    tokens: tp.List[tc.Token] = []
    errored = False
    while current < len(source):
        literal: tp.Optional[lt.LoxLiteral] = None
        char = source[current]
        if char in {"!", "=", "<", ">"}:
            try:
                if source[current + 1] == "=":
                    current += 1
                    char += "="
            except IndexError:
                pass
        elif source[current : current + 2] == "//":
            char = "//"
            try:
                current = source.index("\n", current)
            except ValueError:
                break
            line += 1
        elif source[current : current + 2] == "/*":
            char = "/*"
            start_comment = current
            try:
                current = source.index("*/", start_comment) + 1
            except ValueError:
                break
            line += source.count("\n", start_comment, current)
        elif char == "\n":
            line += 1
        elif char == '"':
            next_p = source.find('"', current + 1)
            if next_p == -1:
                error(line, "Unterminated string literal")
                errored = True
                break
            literal = source[current + 1 : next_p]
            current = next_p
            char = f'"{literal}"'
        if char.isdigit():
            char = ""
            try:
                while lu.is_lox_number(source[current]):
                    char += source[current]
                    current += 1
            except IndexError:
                pass
            literal = float(char)
        elif char.isalpha() or char[0] == "_":
            char = ""
            try:
                while source[current].isalnum() or source[current] == "_":
                    char += source[current]
                    current += 1
            except IndexError:
                pass
            literal = const.VALUE_WORDS.get(char)
        else:
            current += 1

        token_type = to_token_type(char, line)
        if token_type is None:
            errored = True
        elif token_type != tt.EMPTY:
            tokens.append(tc.Token(token_type, char, literal, line))

    return le.ErrorReturns.SCAN_ERROR if errored else tokens
