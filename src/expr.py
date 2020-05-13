from __future__ import annotations
import dataclasses
import typing

import LoxErrors as le
import abstract_execs as ae
import classes as lc
import token_types as tt
import utilities as ut


def evaluate_lox_binary(lox_type: lc.TokenType, left: lc.lox_literal,
                        right: lc.lox_literal) -> lc.lox_literal:
    try:
        if lox_type is tt.MINUS:
            return left - right
        elif lox_type is tt.SLASH:
            return left / right
        elif lox_type is tt.STAR:
            return left * right
        elif lox_type is tt.PLUS:
            return left + right
        elif lox_type is tt.GREATER:
            return left > right
        elif lox_type is tt.GREATER_EQUAL:
            return left >= right
        elif lox_type is tt.LESS:
            return left < right
        elif lox_type is tt.LESS_EQUAL:
            return left <= right
        elif lox_type is tt.EQUAL_EQUAL:
            return left == right
        elif lox_type is tt.BANG_EQUAL:
            return left != right
        else:
            text = f"The operator {lox_type} is not a binary operator"
    except TypeError:
        if isinstance(left, float) and left == int(left):
            return evaluate_lox_binary(lox_type, int(left), right)
        elif isinstance(right, float) and right == int(right):
            return evaluate_lox_binary(lox_type, left, int(right))
        else:
            text = (f"The operator {lox_type} does not support lox types"
                    f" {ut.lox_type(left)} and {ut.lox_type(right)}")
    raise TypeError(text)


def evaluate_lox_unary(lox_type: lc.TokenType, left: lc.lox_literal) -> lc.lox_literal:
    if lox_type is tt.MINUS:
        return -left
    elif lox_type is tt.BANG:
        return not ut.lox_true(left)
    raise TypeError(f"The operator {lox_type} with type {ut.lox_type(left)}"
                    " does not work in a unary format ")


class Expr(ae.AbstractExec):
    pass


@dataclasses.dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: lc.Token
    right: Expr

    def __str__(self) -> str:
        return ut.parenthesize_expr(self.operator.lexeme, self.left, self.right)

    @property
    def exprs(self) -> typing.Tuple[Expr, Expr]:
        return self.left, self.right

    def _evaluate(self) -> lc.lox_literal:
        lox_type = self.operator.type
        left = self.left._evaluate()
        right = self.right._evaluate()
        line = self.operator.line
        try:
            return evaluate_lox_binary(lox_type, left, right)
        except TypeError:
            message = (f'Infix Operator {self.operator.lexeme} is not supported for the'
                       f' types "{ut.lox_type(left)}" and "{ut.lox_type(right)}"')
        except ZeroDivisionError:
            message = "Division by zero"
        raise le.LoxRuntimeError(line, message)


class Grouping(ae.ExprExecMixin, Expr):

    def __str__(self) -> str:
        return ut.parenthesize_expr("group", self.expression)

    def _evaluate(self) -> lc.lox_literal:
        return self.expression._evaluate()


@dataclasses.dataclass(frozen=True)
class Literal(Expr):
    value: lc.lox_literal

    def __str__(self) -> str:
        return str(self.value)

    def _evaluate(self) -> lc.lox_literal:
        return self.value

    @classmethod
    def from_token(cls, token: lc.Token) -> Literal:
        if token.type is tt.NIL:
            value = lc.nil
        elif token.type is tt.TRUE:
            value = True
        elif token.type is tt.FALSE:
            value = False
        elif token.type in {tt.NUMBER, tt.STRING}:
            value = token.literal
        else:
            raise ValueError("The token doesn't have the token.type")
        return cls(value)


@dataclasses.dataclass(frozen=True)
class Unary(Expr):
    operator: lc.Token
    right: Expr

    def __str__(self) -> str:
        return ut.parenthesize_expr(self.operator.lexeme, self.right)

    @property
    def exprs(self) -> typing.Tuple[Expr]:
        return self.right,

    def _evaluate(self) -> lc.lox_literal:
        right = self.right._evaluate()
        line = self.operator.line
        try:
            return evaluate_lox_unary(self.operator.type, right)
        except TypeError:
            pass
        message = (f'Unary Operator {self.operator.lexeme} is not'
                   f' supported for the type "{ut.lox_type(right)}"')
        raise le.LoxRuntimeError(line, message)


class ErrorExpr(ae.ErrorExecMixin, Expr):
    pass
