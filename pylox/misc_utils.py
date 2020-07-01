from __future__ import annotations

import itertools
import typing as tp

# TODO: Put these functions in some separate utilities repo?

T = tp.TypeVar("T")
KT = tp.TypeVar("KT")


def peek_iter(iterable: tp.Iterator[T]) -> tp.Tuple[T, tp.Iterator[T]]:
    value = next(iterable)
    return (value, itertools.chain((value,), iterable))


# Modified, original from the itertools docs
# https://docs.python.org/3.8/library/itertools.html
def pairwise(iterable: tp.Iterable[T]) -> tp.Iterator[tp.Tuple[T, T]]:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..., (sl, None)"""
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.zip_longest(a, b)


def removeprefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def inclusive_takewhile(
    pred: tp.Callable[[T], bool], iterable: tp.Iterable[T]
) -> tp.Iterator[T]:
    for i in iterable:
        yield i
        if pred(i):
            return


def exc_chain(
    exception: tp.Type[BaseException],
    functions: tp.Iterable[tp.Callable[..., T]],
    *args: object,
    **kwargs: object
) -> T:
    for func in functions:
        try:
            return func(*args, **kwargs)
        except exception as exc:
            new_exc = exc
    raise new_exc


@tp.overload
def get(seq: tp.Sequence[KT], index: int) -> tp.Optional[KT]:
    ...


@tp.overload
def get(seq: tp.Sequence[KT], index: int, default: T) -> tp.Union[T, KT]:
    ...


def get(seq, index, default=None):
    try:
        return seq[index]
    except IndexError:
        return default


def reverse_enum(iterable: tp.Sequence[T]) -> tp.Iterator[tp.Tuple[int, T]]:
    yield from zip(range(len(iterable) - 1, -1, -1), reversed(iterable))
