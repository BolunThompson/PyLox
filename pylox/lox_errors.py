from __future__ import annotations

import enum
import inspect
import sys
import typing as tp

import pylox.misc_utils as mu
import pylox.token_classes as tc

DEFAULT_ERROR = "Something very wrong has happened"

ErrorLine = tp.Union[int, str]


class ReturnsNT(tp.NamedTuple):
    code: int
    type: str


class ErrorReturns(ReturnsNT, enum.Enum):
    SUCCESS = ReturnsNT(0, "Success")
    ERROR = ReturnsNT(70, "Error")
    SCAN_ERROR = PARSE_ERROR = RESOLVER_ERROR = ReturnsNT(65, "Syntax Error")
    FILE_ERROR = ReturnsNT(66, "File Error")
    RUNTIME_ERROR = ReturnsNT(70, "Runtime Error")

    def error(self) -> bool:
        return self is not self.SUCCESS


# TODO: Refactor global state out?
# This is meant to incremented when a line goes past when dealing with
# multiple pieces of source code (e.g in the REPL)
line_inc = 0


def error(
    line: ErrorLine,
    message: str = DEFAULT_ERROR,
    error_type: ErrorReturns = ErrorReturns.ERROR,
    *,
    raw_line: bool = False,
) -> None:
    if isinstance(line, int):
        line += line_inc
    elif not raw_line:
        line += f" (after line {line_inc})"
    print(f"[line: {line}] {error_type.value.type}: {message}", file=sys.stderr)


def token_line(mixed_tokens: tp.Iterable[tp.Any]) -> int:
    """
    Helper function for getting the line from a list of of mixed tokens.
    """

    def process_key(key: tp.Any) -> int:
        if isinstance(key, tc.Token):
            return key.line
        try:
            return token_line(key)
        except TypeError:
            return 0

    return max(mixed_tokens, key=process_key, default=0)


def keyboard_interrupt_error(
    error_type: ErrorReturns, line: tp.Optional[ErrorLine] = None
) -> None:
    raw_line = True
    if line is None:
        line = f"estimate {token_line(inspect.trace()[-1][0].f_locals.values())}"
    elif line == 0:
        line = "unknown"
        raw_line = False
    print()
    error(line, "Keyboard Interrupt", error_type, raw_line=raw_line)


class LoxRuntimeError(Exception):
    """ Always caught """

    line: ErrorLine
    message: str
    ignore: bool

    def __init__(
        self,
        line: ErrorLine = "unknown",
        message: str = DEFAULT_ERROR,
        ignore: bool = False,
    ) -> None:
        self.line = line or "unknown"
        self.message = message
        self.ignore = ignore

    def error(self) -> None:
        if not self.ignore:
            error(self.line, self.message, ErrorReturns.RUNTIME_ERROR)


class KeyLoxRuntimeError(LoxRuntimeError, KeyError):
    """
    Subclass of LoxRuntimeError meant for use where it should
    be able to be caught as a KeyError
    """
