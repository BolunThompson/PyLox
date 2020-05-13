from __future__ import annotations
import typing
import dataclasses
import expr

import LoxErrors as le
from classes import stmt_literal


# This is not a abstract class inheriting from abc.ABC for dataclass compatibility
class AbstractExec:
    def __repr__(self) -> str:
        """ The repr """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Readable representation of the code piece """
        raise NotImplementedError

    def _evaluate(self) -> stmt_literal:
        """ Internally evaluates the code piece. Returns None if it is a statement"""
        raise NotImplementedError

    @property
    def exprs(self) -> typing.Tuple[()]:
        """ Returns the expressions contained in this code piece """
        return ()

    def has_error(self) -> bool:
        """ Returns True if the code piece has an error"""
        for expression in self.exprs:
            if expression.has_error():
                return True
        return False

    def interpret(self) -> typing.Union[
            stmt_literal, typing.Literal[le.ErrorReturns.RUNTIME_ERROR]]:
        try:
            return self._evaluate()
        except le.LoxRuntimeError as lre:
            le.error(lre.line, lre.message)
        return le.ErrorReturns.RUNTIME_ERROR


class ErrorExecMixin:
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return 'error'

    @staticmethod
    def has_error() -> bool:
        return True

    def _evaluate(self) -> typing.NoReturn:
        raise le.LoxRuntimeError()


@dataclasses.dataclass(frozen=True)
class ExprExecMixin:
    expression: expr.Expr

    @property
    def exprs(self) -> typing.Tuple[expr.Expr]:
        return self.expression,
