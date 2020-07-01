from __future__ import annotations

import contextlib
import dataclasses
import typing as tp

import pylox.enviroment as env
import pylox.error_dec as ed
import pylox.functions as fn
import pylox.lox_errors as le
import pylox.misc_utils as mu

if tp.TYPE_CHECKING:
    from pylox import stmt
    import pylox.lox_class as lc
    import pylox.abstract_execs as ae

    TAE = tp.TypeVar("TAE", bound=ae.AbstractExec)


@ed.lox_error_handling(le.ErrorReturns.RESOLVER_ERROR)
def resolve(tree: tp.Sequence[TAE]) -> tp.Union[tp.Sequence[TAE], le.ErrorReturns]:
    scopes = ResolverStack()
    for node in tree:
        node.resolve(scopes)
    return tree if not scopes.errored else le.ErrorReturns.RESOLVER_ERROR


@dataclasses.dataclass
class ResolverStack:
    errored: bool = False
    current_function: fn.FunctionType = fn.FunctionType.NONE
    enclosing_function: fn.FunctionType = fn.FunctionType.NONE
    in_loop: bool = False
    lox_class: tp.Optional[stmt.ClassStmt] = None
    stack: tp.List[tp.Dict[str, bool]] = dataclasses.field(default_factory=list)

    def __getitem__(self, index: int) -> tp.Dict[str, bool]:
        return self.stack[index]

    @contextlib.contextmanager
    def declare(self, token: env.EnvKey) -> tp.Iterator[None]:
        """
        This declares the token at the start of the context manager and
        defines it at the end.
        """
        str_token = env.get_str(token)
        scope: tp.Dict[str, bool] = mu.get(self.stack, -1, {})
        if str_token in scope:
            self.error(
                token, f'Variable "{str_token}" name already declared in this scope.'
            )
        scope[str_token] = False
        try:
            yield
        finally:
            scope[str_token] = True

    @contextlib.contextmanager
    def function(self, func_type: fn.FunctionType) -> tp.Iterator[None]:
        self.enclosing_function = self.current_function
        self.current_function = func_type
        try:
            yield
        finally:
            self.current_function = self.enclosing_function

    @contextlib.contextmanager
    def loop(self) -> tp.Iterator[None]:
        self.in_loop = True
        try:
            yield
        finally:
            self.in_loop = False

    @contextlib.contextmanager
    def scope(self) -> tp.Iterator[tp.Dict[str, bool]]:
        new_scope: tp.Dict[str, bool] = {}
        self.stack.append(new_scope)
        try:
            yield new_scope
        finally:
            self.stack.pop()

    @contextlib.contextmanager
    def new_class(self, name: tp.Optional[stmt.ClassStmt]) -> tp.Iterator[None]:
        self.lox_class, name = name, self.lox_class
        try:
            yield
        finally:
            self.lox_class = name

    def define(self, token: env.EnvKey) -> None:
        """
        Declares and defines the token. Equivalent to running:

        with self.declare(token):
            pass
        """
        with self.declare(token):
            pass

    def error(
        self, token: tp.Union[env.EnvKey, int], message: str, *, raw_line=False
    ) -> None:
        le.error(
            env.get_line(token),
            message,
            le.ErrorReturns.RESOLVER_ERROR,
            raw_line=raw_line,
        )
        self.errored = True
