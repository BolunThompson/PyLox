from __future__ import annotations

import contextlib
import typing as tp
from dataclasses import dataclass
import functools
import pylox.abstract_execs as ae
import pylox.control_exc as ce
import pylox.functions as fn
import pylox.lox_class as lc
import pylox.lox_types as lt
import pylox.lox_utils as lu
import pylox.lox_errors as le

if tp.TYPE_CHECKING:
    import pylox.resolver as rs
    import pylox.token_classes as tc
    from pylox import expr


class ExprStmt(ae.ExprExecMixin, ae.Stmt):
    def evaluate(self) -> None:
        self.expression.evaluate()


class PrintStmt(ae.ExprExecMixin, ae.Stmt):
    def evaluate(self) -> None:
        lu.lox_print(self.expression.evaluate())


@dataclass(frozen=True)
class VarStmt(ae.Stmt):
    name: tc.Token
    initializer: tp.Optional[ae.Expr]

    def evaluate(self) -> None:
        self.environment[self.name] = (
            self.initializer.evaluate() if self.initializer is not None else lt.nil
        )

    @property
    def execs(self) -> tp.Union[tp.Tuple[()], tp.Tuple[ae.Expr]]:
        if self.initializer is None:
            return ()
        return (self.initializer,)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        with scopes.declare(self.name):
            if self.initializer is not None:
                self.initializer.resolve(scopes)


class ErrorStmt(ae.ErrorExec, ae.Stmt):
    pass


@dataclass
class BraceStmt(ae.Stmt):
    stmts: tp.Sequence[ae.Stmt]
    function_scope: bool = False

    def evaluate(self) -> None:
        manager: tp.Any = (
            self.environment.scope
            if not self.function_scope
            else contextlib.nullcontext
        )
        with manager():
            for stmt in self.stmts:
                stmt.evaluate()

    @property
    def execs(self) -> tp.Sequence[ae.Stmt]:
        return self.stmts

    def resolve(self, scopes: rs.ResolverStack) -> None:
        manager: tp.Any = scopes.scope if not self.function_scope else contextlib.nullcontext
        with manager():
            for node in self.stmts:
                node.resolve(scopes)


@dataclass(frozen=True)
class IfStmt(ae.Stmt):
    condition: ae.Expr
    then_branch: ae.Stmt
    else_branch: tp.Optional[ae.Stmt]

    @property
    def execs(
        self,
    ) -> tp.Union[tp.Tuple[ae.Expr, ae.Stmt], tp.Tuple[ae.Expr, ae.Stmt, ae.Stmt]]:
        if self.else_branch is None:
            return (self.condition, self.then_branch)
        return (self.condition, self.then_branch, self.else_branch)

    def evaluate(self) -> None:
        if lu.lox_true(self.condition.evaluate()):
            self.then_branch.evaluate()
        elif self.else_branch is not None:
            self.else_branch.evaluate()

    def __str__(self) -> str:
        cls = type(self).__name__
        return f"{cls} {self.condition} [{self.then_branch}, {self.else_branch}]"


@dataclass(frozen=True)
class WhileStmt(ae.Stmt):
    condition: ae.Expr
    body: ae.Stmt

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.condition} [{self.body}]"

    @property
    def execs(self) -> tp.Tuple[ae.AbstractExec, ae.AbstractExec]:
        return (self.condition, self.body)

    def evaluate(self) -> None:
        while lu.lox_true(self.condition.evaluate()):
            try:
                self.body.evaluate()
            except ce.LoxBreakError:
                break

    def resolve(self, scopes: rs.ResolverStack) -> None:
        with scopes.loop():
            self.condition.resolve(scopes)
            self.body.resolve(scopes)


class NullStmt(ae.Stmt):
    def evaluate(self) -> None:
        pass


@dataclass(frozen=True)
class BreakStmt(ae.Stmt):
    token: tc.Token

    def evaluate(self) -> tp.NoReturn:
        raise ce.LoxBreakError(self.token.line)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        if not scopes.in_loop:
            scopes.error(self.token.line, "Break statement outside of a loop")


@dataclass(frozen=True)
class ReturnStmt(ae.Stmt):
    keyword: tc.Token
    value: ae.Expr

    def evaluate(self) -> tp.NoReturn:
        raise ce.LoxReturnError(self.value.evaluate(), self.keyword.line)

    @property
    def execs(self) -> tp.Tuple[ae.Expr]:
        return (self.value,)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        if scopes.current_function is fn.FunctionType.NONE:
            scopes.error(self.keyword.line, "Cannot return from top-level code.")
        if getattr(self.value, "value", None) is not lt.nil:
            if scopes.current_function is fn.FunctionType.INITIALIZER:
                scopes.error(
                    self.keyword.line, "Cannot return a value from an initializer."
                )
            self.value.resolve(scopes)


# TODO: Consider changing the function and class statements to an expression returning
# the function or class and having a side effect of defining the object in scope?
# Anonymous functions could be written by not providing a name,
# e.g "fun (x, y) {...}"
@dataclass(frozen=True)
class FunctionStmt(ae.Stmt):
    function: fn.LoxFunction

    def evaluate(self) -> None:
        self.function.closure = self.environment.maps[0]
        self.environment[self.function.name] = self.function

    @classmethod
    def from_params(
        cls, params: tp.Sequence[tc.Token], body: ae.Stmt, name: tc.Token
    ) -> FunctionStmt:
        return cls(fn.LoxFunction(params, body, name.lexeme))

    @property
    def execs(self) -> tp.Tuple[ae.Stmt]:
        return (self.function.body,)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        scopes.define(self.function.name)
        self.function.resolve(scopes, fn.FunctionType.FUNCTION)


@dataclass(frozen=True)
class ClassStmt(ae.Stmt):
    lox_class: lc.LoxClass
    super_class_var: tp.Optional[expr.Variable]

    def resolve(self, scopes: rs.ResolverStack) -> None:
        with scopes.new_class(self):
            scopes.define(self.lox_class.name)
            if self.super_class_var is not None:
                self.super_class_var.resolve(scopes)
            self.lox_class.resolve(scopes)

    def evaluate(self) -> None:
        self.lox_class.super_class = self.super_class
        self.environment[self.lox_class.name] = self.lox_class

    @classmethod
    def from_params(
        cls,
        name: tc.Token,
        super_class: tp.Optional[expr.Variable],
        methods: tp.Iterable[fn.LoxFunction],
        static_methods: tp.Iterable[fn.LoxFunction],
        getter_methods: tp.Iterable[fn.LoxFunction],
    ) -> ClassStmt:
        return cls(
            lc.LoxClass(
                name.lexeme,
                None,
                {method.name: method for method in methods},
                {method.name: method for method in static_methods},
                {method.name: method for method in getter_methods},
            ),
            super_class,
        )

    @property
    def execs(self) -> tp.List[ae.Stmt]:
        return [func.body for func in self.lox_class.functions]

    @functools.cached_property
    def super_class(self) -> tp.Optional[lc.LoxClass]:
        if self.super_class_var is None:
            return None
        value = self.super_class_var.evaluate()
        if not isinstance(value, lc.LoxClass):
            raise le.LoxRuntimeError(
                self.super_class_var.name.line, "Superclass must be a class"
            )
        return value
