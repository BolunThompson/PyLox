from __future__ import annotations

import itertools
import typing as tp
from collections import defaultdict

from more_itertools import peekable

import pylox.misc_utils as mu
import pylox.token_classes as tc
from pylox.token_classes import TokenType as tt


def null_split(tokens: tp.Iterator[tc.Token]) -> tp.Tuple[()]:
    next(tokens)
    return ()


def matched_braces(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[tc.Token]:
    level = 0
    found_brace = False
    for token in tokens:
        yield token
        if token.type is tt.LEFT_BRACE:
            level += 1
            found_brace = True
        elif token.type is tt.RIGHT_BRACE:
            level -= 1
        if found_brace and level == 0:
            return


def a_match_braces(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[peekable[tc.Token]]:
    tokens = peekable(tokens)
    while tokens:
        yield peekable(matched_braces(tokens))


def parens(iterable: tp.Iterable[tc.Token]) -> tp.Iterator[tc.Token]:
    return mu.inclusive_takewhile(lambda x: x.type is tt.RIGHT_PAREN, iterable)


def if_stmt(tokens: peekable[tc.Token]) -> tp.Iterator[tc.Token]:
    yield from cond_stmt(tokens)
    if tokens.peek(tc.sentinel_token).type is tt.ELSE:
        yield next(tokens)
        yield from split_stmt(tokens)


def cond_stmt(tokens: peekable[tc.Token]) -> tp.Iterator[tc.Token]:
    yield from parens(iterable=tokens)
    yield from split_stmt(tokens)


def split_stmt(tokens: peekable[tc.Token]) -> tp.Iterable[tc.Token]:
    return SPLIT_TOKENS_FUNCS[getattr(tokens.peek(None), "type", None)](tokens)


def expr_split(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[tc.Token]:
    return itertools.takewhile(lambda x: x.type is not tt.SEMICOLON, tokens)


SplitFunc = tp.Callable[[peekable], tp.Iterable[tc.Token]]


SPLIT_TOKENS_FUNCS: tp.DefaultDict[tp.Optional[tc.TokenType], SplitFunc] = defaultdict(
    lambda: expr_split,
    {
        tt.SEMICOLON: null_split,
        tt.LEFT_BRACE: matched_braces,
        tt.CLASS: matched_braces,
        tt.WHILE: cond_stmt,
        tt.FOR: cond_stmt,
        tt.FUN: matched_braces,
        tt.IF: if_stmt,
        None: lambda _: (),
    },
)


def split_tokens(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[tp.Iterable[tc.Token]]:
    p_tokens = peekable(tokens)
    while p_tokens:
        yield split_stmt(p_tokens)
