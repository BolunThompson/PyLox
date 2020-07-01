from __future__ import annotations

import abc
import typing as tp
from dataclasses import dataclass, field

import pylox.enviroment as env
import pylox.lox_builtins as lb
import pylox.lox_errors as le
from pylox import results
import pylox.misc_utils as mu

if tp.TYPE_CHECKING:
    import pylox.resolver as rs
    import pylox.lox_types as lt
    import pylox.token_classes as tc


class AbstractExec(abc.ABC):
    environment: tp.ClassVar[env.Environment] = env.Environment(lb.BUILTINS)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractmethod
    def evaluate(self) -> lt.StmtLiteral:
        """
        Evaluates the node. Returns None if it is a statement.
        If you want to execute the AST, call AbstractExec.interpret
        """

    def resolve(self, scopes: rs.ResolverStack) -> None:
        """ Resolves the node."""
        for node in self.execs:
            node.resolve(scopes)

    @property
    def execs(self) -> tp.Sequence[AbstractExec]:
        """
        Returns the AbstractExecs contained in this node
        """
        return ()

    def has_error(self) -> bool:
        """ Returns True if the code piece has an error"""
        return has_error(self.execs)

    def interpret(self) -> results.ResultNT:
        try:
            return results.ResultNT(self.evaluate())
        except le.LoxRuntimeError as lre:
            lre.error()
        return results.ResultNT(None, le.ErrorReturns.RUNTIME_ERROR)


class ErrorExec(AbstractExec):
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
        return "error"

    def has_error(self) -> bool:
        return True

    def evaluate(self) -> tp.NoReturn:
        raise le.LoxRuntimeError(ignore=True)


class Stmt(AbstractExec):
    def __str__(self) -> str:
        return f"{type(self).__name__} {self.execs}"

    @abc.abstractmethod
    def evaluate(self) -> None:
        pass


class Expr(AbstractExec):
    @abc.abstractmethod
    def evaluate(self) -> lt.LoxLiteral:
        pass


@dataclass(frozen=True)  # type: ignore
class ExprExecMixin(AbstractExec, abc.ABC):
    expression: Expr

    @property
    def execs(self) -> tp.Tuple[Expr]:
        return (self.expression,)


@dataclass(frozen=True)  # type: ignore
class BinaryExpr(Expr, abc.ABC):
    left: Expr
    operator: tc.Token
    right: Expr

    def __str__(self) -> str:
        return parenthesize_expr(self.operator.lexeme, self.left, self.right)

    @property
    def execs(self) -> tp.Tuple[Expr, Expr]:
        return self.left, self.right


@dataclass  # type: ignore
class VarExpr(Expr, abc.ABC):
    name: tc.Token
    distance: int = field(init=False, default=-1)

    def resolve_local(self, scopes: rs.ResolverStack) -> None:
        for i, scope in mu.reverse_enum(scopes.stack):
            if self.name.lexeme in scope:
                self.distance = i
                return


def has_error(iterable: tp.Iterable[AbstractExec]) -> bool:
    return any(expr.has_error() for expr in iterable)


def parenthesize_expr(name: str, *args: object) -> str:
    str_exprs = " ".join(f"{arg}" for arg in args)
    return f"{name} ({str_exprs})"
