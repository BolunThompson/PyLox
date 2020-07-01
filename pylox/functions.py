from __future__ import annotations

import collections
import dataclasses
import enum
import typing as tp
import itertools
import pylox.control_exc as ce
import pylox.lox_types as lt

if tp.TYPE_CHECKING:
    import pylox.abstract_execs as ae
    import pylox.enviroment as env
    import pylox.token_classes as tc
    import pylox.resolver as rs


class FunctionType(str, enum.Enum):
    NONE = "NONE"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    INITIALIZER = "INITIALIZER"


@dataclasses.dataclass
class LoxFunction(lt.LoxCallable):
    params: tp.Sequence[tc.Token]
    body: ae.Stmt
    name: str
    is_initializer: bool = False
    is_property: bool = False
    closure: env.EnvMapping = dataclasses.field(init=False, default_factory=dict)

    @ce.function_break
    def lox_call(self, arguments: tp.Sequence[lt.LoxLiteral]) -> lt.LoxLiteral:
        assert len(arguments) == self.arity, "Wrong number of arguments passed"
        arg_dict = {name.lexeme: arg for name, arg in zip(self.params, arguments)}
        with self.body.environment.scope(collections.ChainMap(arg_dict, self.closure)):
            try:
                self.body.evaluate()
            except ce.LoxReturnError:
                if not self.is_initializer:
                    raise
                return self.body.environment.index_get("this", 0)
        return lt.nil

    def __str__(self) -> str:
        params = ", ".join(x.lexeme for x in self.params)
        return f"<fn {self.name}({params})>"

    def resolve(
        self, scopes: rs.ResolverStack, func_type: FunctionType, *params: env.EnvKey
    ) -> None:
        with scopes.function(func_type), scopes.scope():
            for param in itertools.chain(self.params, params):
                scopes.define(param)
            self.body.resolve(scopes)

    @property
    def arity(self) -> int:
        return len(self.params)
