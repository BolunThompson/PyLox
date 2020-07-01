from __future__ import annotations

import dataclasses
import inspect
import time
import typing as tp

import pylox.control_exc as ce
import pylox.lox_errors as le
import pylox.lox_types as lt
import pylox.misc_utils as mu
import pylox.lox_class as lc

if tp.TYPE_CHECKING:
    import pylox.functions as fn

    TC = tp.TypeVar("TC", bound=tp.Callable[..., lt.LoxLiteral])


@dataclasses.dataclass(frozen=True)
class LoxNativeFunction(lt.LoxCallable):
    function: tp.Callable  # Should be tp.Callable[<*args: lt.LoxLiteral>, lt.LoxLiter]
    name: str

    @ce.function_break
    def lox_call(self, arguments: tp.Sequence[lt.LoxLiteral]) -> lt.LoxLiteral:
        return self.function(*arguments)

    def __str__(self) -> str:
        return f"<fn native {self.name}>"

    @property
    def arity(self) -> int:
        return len(inspect.signature(self.function).parameters)


BUILTINS: tp.Dict[str, LoxNativeFunction] = {}


def lox_native_function(wrapped: TC) -> TC:
    lox_name = mu.removeprefix(wrapped.__name__, "lox_")
    BUILTINS[lox_name] = LoxNativeFunction(wrapped, lox_name)
    return wrapped


@lox_native_function
def clock() -> float:
    return time.time()


@lox_native_function
def lox_len(string: str) -> float:
    # TODO: Change to a lox method available on strings?
    try:
        return float(len(string))
    except TypeError as exc:
        import pylox.lox_utils as lu

        message = f"Type {lu.lox_type(string)} does not have a length."
        raise le.LoxRuntimeError(message) from exc


@lox_native_function
def lox_input() -> str:
    return input()
