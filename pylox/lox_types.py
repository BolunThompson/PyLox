from __future__ import annotations

import abc
import typing as tp


class _Singleton(type):
    _instances: tp.ClassVar[tp.Dict[_Singleton, object]] = {}

    def __call__(cls, *args: object, **kwargs: object) -> object:
        try:
            return cls._instances[cls]
        except KeyError:
            pass
        instance = super().__call__(*args, **kwargs)
        cls._instances[cls] = instance
        return instance


class NilType(metaclass=_Singleton):
    def __repr__(self) -> str:
        return "nil"


nil = NilType()


class LoxCallable(abc.ABC):
    name: str

    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractmethod
    def lox_call(self, arguments: tp.Sequence[LoxLiteral]) -> LoxLiteral:
        pass

    @classmethod
    def __subclasshook__(cls, subclass) -> tp.Union[tp.Literal[True], NotImplemented]:
        return hasattr(subclass, "lox_call") or NotImplemented

    @property
    @abc.abstractmethod
    def arity(self) -> int:
        pass


if tp.TYPE_CHECKING:
    import pylox.lox_class as lc

    LoxLiteral = tp.Union[
        bool, float, str, NilType, LoxCallable, lc.LoxInstance, lc.LoxClass
    ]
    StmtLiteral = tp.Optional[LoxLiteral]
