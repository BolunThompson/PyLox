from __future__ import annotations

import functools
import typing as tp

import pylox.lox_errors as le
import pylox.lox_types as lt


class LoxReturnError(le.LoxRuntimeError):
    value: lt.LoxLiteral

    def __init__(self, value: lt.LoxLiteral, line: le.ErrorLine = "unknown") -> None:
        super().__init__(line, "Return statement outside of a function")
        self.value = value


class LoxBreakError(le.LoxRuntimeError):
    def __init__(self, line: le.ErrorLine = "unknown") -> None:
        super().__init__(line, "Break statement outside of a loop")

    def runtime_cast(self) -> le.LoxRuntimeError:
        lre = le.LoxRuntimeError()
        lre.__dict__ = self.__dict__
        return lre


def function_break(wrapped: tp.Callable[..., lt.LoxLiteral]) -> tp.Callable:
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs) -> lt.LoxLiteral:
        try:
            return wrapped(*args, **kwargs)
        except LoxBreakError as lbe:
            raise lbe.runtime_cast() from None
        except LoxReturnError as lre:
            return lre.value

    return wrapper
