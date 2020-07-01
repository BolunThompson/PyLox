from __future__ import annotations

import collections
import dataclasses
import typing as tp
import enum
import pylox.enviroment as env
import pylox.functions as fn
import pylox.lox_errors as le
import pylox.lox_types as lt
import pylox.misc_utils as mu
import itertools

if tp.TYPE_CHECKING:
    from pylox import stmt
    import pylox.resolver as rs


@dataclasses.dataclass
class LoxInstance:
    lox_class: LoxClass
    arguments: dataclasses.InitVar[tp.Sequence[lt.LoxLiteral]]
    fields: tp.MutableMapping[str, lt.LoxLiteral] = dataclasses.field(
        default_factory=dict, init=False
    )

    def __post_init__(self, arguments: tp.Sequence[lt.LoxLiteral]) -> None:
        try:
            function = self.lox_class.method_get("init")
        except KeyError:
            pass
        else:
            function.lox_call(arguments)

    def __str__(self) -> str:
        return f"{self.lox_class.name} instance"

    def __getitem__(self, name: env.EnvKey) -> lt.LoxLiteral:
        return mu.exc_chain(
            KeyError, (self.property_get, self.lox_class.method_get), name
        )

    def __setitem__(self, key: env.EnvKey, value: lt.LoxLiteral) -> None:
        self.fields[env.get_str(key)] = value

    def __delitem__(self, key: env.EnvKey) -> None:
        del self.fields[env.get_str(key)]

    def property_get(self, name: env.EnvKey) -> lt.LoxLiteral:
        str_name = env.get_str(name)
        value = self.fields.get(str_name)
        if value is None:
            raise le.KeyLoxRuntimeError(
                env.get_line(name), f'Undefined property, "{name}".'
            )
        if isinstance(value, fn.LoxFunction) and value.is_property:
            value.closure = collections.ChainMap({"this": self}, value.closure)
            return value.lox_call(())
        return value


@dataclasses.dataclass
class LoxClass(lt.LoxCallable, LoxInstance):
    name: str
    methods: tp.Mapping[str, fn.LoxFunction]
    getters: tp.Mapping[str, fn.LoxFunction]
    super_class: tp.Optional[LoxClass]

    def __init__(
        self,
        name: str,
        super_class: tp.Optional[LoxClass],
        methods: tp.Mapping[str, fn.LoxFunction],
        static_methods: tp.Mapping[str, fn.LoxFunction],
        getter_methods: tp.Mapping[str, fn.LoxFunction],
        *,
        lox_class: tp.Optional[LoxClass] = None,
    ) -> None:
        if lox_class is None:
            lox_class = lox_type
        self.super_class = super_class
        self.lox_class = lox_class
        self.name = name
        self.methods = methods
        self.fields = dict(static_methods)
        self.getters = getter_methods

    @property
    def arity(self) -> int:
        if "init" in self.methods:
            return self.methods["init"].arity
        return 0

    def __str__(self) -> str:
        return f"{self.name} class"

    def lox_call(self, arguments: tp.Sequence[lt.LoxLiteral]) -> LoxInstance:
        return LoxInstance(self, arguments)

    def resolve(self, scopes: rs.ResolverStack) -> None:
        if self.super_class is not None:
            if self.super_class.name == self.name:
                scopes.error(
                    f"Start of class {self.name}",
                    "A class cannot inherit from itself.",
                    raw_line=True,
                )
            self.super_class.resolve(scopes)
        for method in self.functions:
            if method.name == "init":
                func_type = fn.FunctionType.INITIALIZER
                method.is_initializer = True
            else:
                func_type = fn.FunctionType.METHOD
                method.is_initializer = False
            if self.super_class is not None:
                method.resolve(scopes, func_type, "this", "super")
            else:
                method.resolve(scopes, func_type, "this")

    @property
    def functions(self) -> tp.Iterable[fn.LoxFunction]:
        return itertools.chain(
            self.methods.values(),
            self.getters.values(),
            (x for x in self.fields.values() if isinstance(x, fn.LoxFunction)),
        )

    def method_get(self, name: env.EnvKey) -> fn.LoxFunction:
        method = self.methods.get(env.get_str(name))
        if method is not None:
            if self.super_class is not None:
                method.closure = collections.ChainMap(
                    {"this": self, "super": self.super_class}, method.closure
                )
            else:
                method.closure = collections.ChainMap({"this": self}, method.closure)
            return method
        if self.super_class is not None:
            return self.super_class.method_get(name)
        raise le.KeyLoxRuntimeError(env.get_line(name), f'Undefined method, "{name}".')


class MethodType(str, enum.Enum):
    BOUND = "BOUND"
    STATIC = "STATIC"
    PROPERTY = "PROPERTY"


class MethodNT(tp.NamedTuple):
    function: tp.Union[stmt.FunctionStmt, stmt.ErrorStmt]
    type: MethodType


lox_type = LoxClass("type", None, {}, {}, {}, lox_class="TEMP")  # type: ignore
lox_type.lox_class = lox_type
