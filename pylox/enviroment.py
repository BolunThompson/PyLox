from __future__ import annotations

import collections
import contextlib
import typing as tp

import pylox.lox_errors as le

if tp.TYPE_CHECKING:
    import pylox.token_classes as tc
    import pylox.lox_types as lt

    EnvKey = tp.Union[tc.Token, str]
    EnvMapping = tp.MutableMapping[str, lt.LoxLiteral]
    EnvDict = tp.Union[tp.Dict[str, lt.LoxLiteral], tp.ChainMap[str, lt.LoxLiteral]]


def get_str(key: EnvKey) -> str:
    return getattr(key, "lexeme", key)


def get_line(key: tp.Union[EnvKey, int]) -> le.ErrorLine:
    return getattr(key, "line", key if isinstance(key, int) else "unknown")


class Environment(collections.ChainMap):
    # TODO: Consider replacing the list in self.maps with a deque?
    __slots__ = ("maps",)
    maps: tp.List[EnvDict]  # type: ignore

    def __contains__(self, key: tp.Any) -> bool:
        return super().__contains__(get_str(key))

    def __getitem__(self, token: EnvKey) -> lt.LoxLiteral:
        return super().__getitem__(get_str(token))

    def __setitem__(self, token: EnvKey, value: lt.LoxLiteral) -> None:
        super().__setitem__(get_str(token), value)

    def __delitem__(self, key: EnvKey) -> None:
        super().__delitem__(get_str(key))

    def __missing__(self, key: EnvKey, message: tp.Optional[str] = None) -> tp.NoReturn:
        if message is None:
            message = f'Undefined variable "{get_str(key)}"'
        raise le.KeyLoxRuntimeError(get_line(key), message)

    @contextlib.contextmanager
    def scope(self, lox_locals: EnvDict = None) -> tp.Iterator[EnvDict]:
        if lox_locals is None:
            lox_locals = {}
        self.maps.insert(0, lox_locals)
        try:
            yield lox_locals
        finally:
            del self.maps[0]

    def index_get(self, key: EnvKey, index: int) -> lt.LoxLiteral:
        try:
            return self.maps[index][get_str(key)]
        except KeyError:
            pass
        return self.__missing__(key)

    def index_assign(
        self, name: EnvKey, value: lt.LoxLiteral, index: int
    ) -> lt.LoxLiteral:
        if get_str(name) in self.maps[index]:
            self.maps[index][get_str(name)] = value
            return value
        return self.__missing__(name)
