from __future__ import annotations

import functools
import typing as tp

import pylox.lox_errors as le
from pylox import results

if tp.TYPE_CHECKING:
    import pylox.token_classes as tc
    import pylox.abstract_execs as ae

    TAE = tp.TypeVar("TAE", bound=ae.AbstractExec)
    TER = tp.TypeVar("TER", bound=tp.Type[ae.ErrorExec])
    AbsExecCall = tp.Callable[..., TAE]
    AbsExecDec = tp.Callable[[AbsExecCall], AbsExecCall]

Callable = tp.Callable[..., object]  # To satify mypy --strict and pyright
Decorator = tp.Callable[[Callable], Callable]


def propogate_lox_error(wrapped: ReturnListCallable) -> ReturnListCallable:
    @functools.wraps(wrapped)
    def wrapper(*args: object, **kwargs: object) -> results.ReturnList:
        arg = args[0]
        if isinstance(arg, results.ReturnList):
            return arg
        if isinstance(arg, le.ErrorReturns):
            return results.ReturnList(status=arg)
        return wrapped(*args, **kwargs)

    return wrapper


ReturnListCallable = tp.Callable[..., results.ReturnList]
ReturnListDec = tp.Callable[[ReturnListCallable], ReturnListCallable]


def lox_keyboard_interrupt(
    error_type: le.ErrorReturns, line: tp.Optional[int] = None
) -> ReturnListDec:
    def decorator(wrapped: ReturnListCallable) -> ReturnListCallable:
        @functools.wraps(wrapped)
        def wrapper(*args: object, **kwargs: object) -> results.ReturnList:
            try:
                return wrapped(*args, **kwargs)
            except KeyboardInterrupt:
                le.keyboard_interrupt_error(error_type, line)
            return results.ReturnList(status=error_type)

        return wrapper

    return decorator


ReturnCallable = tp.Callable[..., results.ReturnList]


def lox_error_handling(
    error_type: le.ErrorReturns, line: tp.Optional[int] = None
) -> ReturnListCallable:
    # TODO: Fix type: ignore
    return lox_keyboard_interrupt(error_type, line)(propogate_lox_error)  # type: ignore


def error_print(message: str, error_exec: TER) -> AbsExecDec:
    def decorator(wrapped: AbsExecCall) -> AbsExecCall:
        @functools.wraps(wrapped)
        def wrapper(
            tokens: tc.TokenSeq, *args: object, **kwargs: object
        ) -> ae.AbstractExec:
            result = wrapped(tokens, *args, **kwargs)
            if result.has_error():
                le.error(tokens[0].line, message)
                return error_exec()
            return result

        return wrapper

    return decorator
