import typing
import enum
import sys

DEFAULT_ERROR = "Something very wrong has happened"

line_increment = 0


def error(line: typing.Optional[int] = None, message: str = DEFAULT_ERROR,
          error_type: str = "Error") -> None:
    line = "unknown" if line is None else line+line_increment
    print(f"[line {line}] {error_type}: {message}", file=sys.stderr)


class LoxRuntimeError(Exception):
    """ Always caught """
    line: typing.Optional[int]
    message: str

    def __init__(self, line: typing.Optional[int] = None,
                 message: str = DEFAULT_ERROR):
        super().__init__()  # Purposely empty
        self.message = message
        self.line = line

    def error(self) -> None:
        error(self.line, self.message)


class ErrorReturns(enum.IntEnum):
    SCAN_ERROR = 65
    PARSE_ERROR = 65
    RUNTIME_ERROR = 70
