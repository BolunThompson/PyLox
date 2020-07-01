from __future__ import annotations

import typing as tp
from dataclasses import dataclass

import pylox.abstract_execs as ae
import pylox.lox_class as lc
import pylox.lox_errors as le
import pylox.lox_eval as lev
import pylox.lox_types as lt
import pylox.lox_utils as lu
import pylox.misc_utils as mu
from pylox.token_classes import TokenType as tt

if tp.TYPE_CHECKING:
    from pylox import stmt
    import pylox.token_classes as tc
    import pylox.resolver as rs


class Binary(ae.BinaryExpr):
    def evaluate(self) -> lt.LoxLiteral:
        lox_type = self.operator.type
        left = self.left.evaluate()
        right = self.right.evaluate()
        try:
            return lev.evaluate_lox_binary(lox_type, left, right)
        except TypeError:
            message = (
                f'Infix Operator "{self.operator.lexeme}" is not supported for the'
                f' types "{lu.lox_type(left)}" and "{lu.lox_type(right)}"'
            )
        except ZeroDivisionError:
            message = "Division by zero"
        raise le.LoxRuntimeError(self.operator.line, message)


class Grouping(ae.ExprExecMixin, ae.Expr):
    def __str__(self) -> str:
        return ae.parenthesize_expr("group", self.expression)

    def evaluate(self) -> lt.LoxLiteral:
        return self.expression.evaluate()


@dataclass(frozen=True)
class Literal(ae.Expr):
    value: lt.LoxLiteral

    def __str__(self) -> str:
        return str(self.value)

    def evaluate(self) -> lt.LoxLiteral:
        return self.value


@dataclass(frozen=True)
class Unary(ae.Expr):
    operator: tc.Token
    right: ae.Expr

    def __str__(self) -> str:
        return ae.parenthesize_expr(self.operator.lexeme, self.right)

    @property
    def execs(self) -> tp.Tuple[ae.Expr]:
        return (self.right,)

    def evaluate(self) -> lt.LoxLiteral:
        right = self.right.evaluate()
        try:
            return lev.evaluate_lox_unary(self.operator.type, right)
        except TypeError as exc:
            message = (
                f"Unary Operator {self.operator.lexeme} is not"
                f' supported for the type "{lu.lox_type(right)}"'
            )
            raise le.LoxRuntimeError(self.operator.line, message) from exc


class Variable(ae.VarExpr):
    def __str__(self) -> str:
        return self.name.lexeme

    def evaluate(self) -> lt.LoxLiteral:
        return self.environment.index_get(self.name, self.distance)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        if mu.get(scopes.stack, -1, {}).get(self.name.lexeme) is False:
            message = "Cannot read local variable in its own initializer."
            scopes.error(self.name.line, message)
        self.resolve_local(scopes)


@dataclass
class Assign(ae.VarExpr):
    value: ae.Expr  # type: ignore

    def __str__(self) -> str:
        return ae.parenthesize_expr(self.name.lexeme, self.value)

    def evaluate(self) -> lt.LoxLiteral:
        return self.environment.index_assign(
            self.name, self.value.evaluate(), self.distance
        )

    @property
    def execs(self) -> tp.Tuple[ae.Expr]:
        return (self.value,)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        self.value.resolve(scopes)
        self.resolve_local(scopes)


class Logical(ae.BinaryExpr):
    def evaluate(self) -> lt.LoxLiteral:
        assert self.operator.type in {
            tt.OR,
            tt.AND,
        }, f"{self.operator} is not a logical expression"
        left = self.left.evaluate()
        if self.operator.type is tt.OR:
            if lu.lox_true(left):
                return left
            return self.right.evaluate()
        if not lu.lox_true(left):
            return left
        return self.right.evaluate()


@dataclass(frozen=True)
class Call(ae.Expr):
    callee: ae.Expr
    paren: tc.Token
    arguments: tp.Sequence[ae.Expr]

    def evaluate(self) -> lt.LoxLiteral:
        callee = self.callee.evaluate()
        if not isinstance(callee, lt.LoxCallable):
            message = f"{lu.lox_str(callee, repl=True)} is not callable."
            raise le.LoxRuntimeError(self.paren.line, message)
        arguments = [arg.evaluate() for arg in self.arguments]
        if callee.arity != len(arguments):
            message = f"Expected {callee.arity} arguments but got {len(arguments)}."
            raise le.LoxRuntimeError(self.paren.line, message)
        try:
            return callee.lox_call(arguments)
        except le.LoxRuntimeError as lre:
            if lre.line == "unknown":
                lre.line = self.paren.line
            raise lre

    def __str__(self) -> str:
        return ae.parenthesize_expr(str(self.callee), *self.arguments)

    @property
    def execs(self) -> tp.Tuple[ae.Expr, ...]:
        return (self.callee,) + tuple(self.arguments)


class ErrorExpr(ae.ErrorExec, ae.Expr):
    pass


@dataclass(frozen=True)
class Get(ae.Expr):
    object: ae.Expr
    name: tc.Token

    @property
    def execs(self) -> tp.Tuple[ae.Expr]:
        return (self.object,)

    def evaluate(self) -> lt.LoxLiteral:
        parent = self.object.evaluate()
        if isinstance(parent, lc.LoxInstance):
            return parent[self.name]
        raise le.LoxRuntimeError(self.name.line, "Only instances have properties")

    def __str__(self) -> str:
        return ae.parenthesize_expr(self.name.lexeme, self.object)


@dataclass(frozen=True)
class Set(ae.Expr):
    assignee: Get
    value: ae.Expr

    @property
    def execs(self) -> tp.Tuple[ae.Expr, ...]:
        return self.assignee.execs + (self.value,)

    def __str__(self) -> str:
        return ae.parenthesize_expr(str(self.assignee), self.value)

    def evaluate(self) -> lt.LoxLiteral:
        target = self.assignee.object.evaluate()
        if not isinstance(target, lc.LoxInstance):
            raise le.LoxRuntimeError(
                self.assignee.name.line, "Only instances have fields."
            )
        value = self.value.evaluate()
        target[self.assignee.name] = value
        return value


@dataclass
class Super(ae.VarExpr):
    method: tc.Token
    lox_class: tp.Optional[stmt.ClassStmt] = None

    def __str__(self):
        return f"{{{self.lox_class}}} super.{self.method.lexeme}"

    def resolve(self, scopes: rs.ResolverStack) -> None:
        if scopes.lox_class is None:
            scopes.error(self.name, "Super used outside of a class")
        elif scopes.lox_class.super_class is None:
            scopes.error(self.name, "Super used in a class without a superclass")
        else:
            self.lox_class = scopes.lox_class

    def evaluate(self) -> lt.LoxLiteral:
        if self.lox_class is None or self.lox_class.super_class is None:
            raise le.LoxRuntimeError(self.name.line, "Super used without a superclass")
        return self.lox_class.super_class.method_get(self.method)

    @property
    def execs(self) -> tp.Union[tp.Tuple[stmt.ClassStmt], tp.Tuple[()]]:
        return (self.lox_class,) if self.lox_class is not None else ()


def from_token(token: tc.Token) -> tp.Union[Literal, Variable]:
    if token.type is tt.IDENTIFIER:
        return Variable(token)
    if token.literal is None:
        raise ValueError(f"Invalid token {repr(token)} was passed.")
    return Literal(token.literal)
