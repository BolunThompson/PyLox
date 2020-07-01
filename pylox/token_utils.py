from __future__ import annotations

import functools
import itertools
import typing as tp

from more_itertools import peekable

import pylox.lox_errors as le
import pylox.token_classes as tc
from pylox import const
from pylox.token_classes import TokenType as tt
import pylox.misc_utils as mu

error = functools.partial(le.error, error_type=le.ErrorReturns.PARSE_ERROR)


def token_find_gen_ignore_first(
    tokens: tp.Iterable[tc.Token], token_types: tp.Container[tc.TokenType]
) -> tp.Iterator[int]:
    found_token = False
    for i, token in non_parens(tokens):
        if found_token and token.type in token_types:
            found_token = False
            yield i
        if token.type not in token_types:
            found_token = True


def token_find_index(
    tokens: tp.Iterable[tc.Token], token_types: tp.Container[tc.TokenType]
) -> tp.Iterator[int]:
    return (token[0] for token in enumerate(tokens) if token[1].type in token_types)


Matched = tp.Literal["left", "right", "matched"]


def matched_paren(
    tokens: tp.Iterable[tc.Token],
    left: tc.TokenType = tt.LEFT_PAREN,
    right: tc.TokenType = tt.RIGHT_PAREN,
) -> Matched:
    paren_level = sum({left: 1, right: -1}.get(token.type, 0) for token in tokens)
    if paren_level > 0:
        return "left"
    if paren_level < 0:
        return "right"
    return "matched"


def at_end(tokens: tp.Iterable[tc.Token]) -> bool:
    return any(token.type is tt.EOF for token in tokens)


class EnumeratedTokensNT(tp.NamedTuple):
    position: int
    token: tc.Token


def non_parens(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[EnumeratedTokensNT]:
    paren_level = 0
    for i, token in enumerate(tokens):
        if token.type is tt.RIGHT_PAREN:
            paren_level += 1
        elif token.type is tt.LEFT_PAREN:
            paren_level -= 1
        elif paren_level == 0:
            yield EnumeratedTokensNT(i, token)


def synchronize(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[tc.Token]:
    iter_tokens = iter(tokens)
    for token in iter_tokens:
        if token.type in const.SYNC_TOKENS:
            return iter_tokens
    return iter_tokens


MATCH_PARENS: tp.Tuple[tp.Tuple[tc.TokenType, tc.TokenType], ...] = (
    (tt.LEFT_PAREN, tt.RIGHT_PAREN),
    (tt.RIGHT_BRACE, tt.LEFT_BRACE),
)


def check_matching(tokens: tc.TokenSeq,) -> bool:
    """
    Checks if the parentheses match and if true, prints an error.
    Returns False if it errored, else True.
    """

    def match_error(token_type: tc.TokenType) -> None:
        token = next(token for token in reversed(tokens) if token.type == token_type)
        error(token.line, f'Unmatched "{token.lexeme}"')

    return_value = True
    for left, right in MATCH_PARENS:
        matched = matched_paren(tokens, left, right)
        if matched == "left":
            match_error(left)
        elif matched == "right":
            match_error(right)
        else:
            continue
        return_value = False
    return return_value


def token_str(tokens: tp.Iterable[tc.Token]) -> str:
    return "".join(token.lexeme for token in tokens)


def paren_check(tokens: tc.TokenSeq) -> bool:
    """
    Checks if the parenthesis are equal, and prints an error if they aren't.
    Returns False on an error, and True otherwise.
    Assumes first non paren token is included
    """
    if tokens[1].type is not tt.LEFT_PAREN:
        error(tokens[1].line, f'Expect "(" after "{tokens[0].lexeme}".')
    elif tokens[-1].type is not tt.RIGHT_PAREN:
        error(tokens[-1].line, 'Expect ")" after condition.')
    else:
        return True
    return False


def specified_token_split(
    tokens: tp.Iterable[tc.Token], t_type: tc.TokenType
) -> tp.Iterator[peekable[tc.Token]]:
    p_tokens = peekable(tokens)
    while p_tokens:
        yield peekable(itertools.takewhile(lambda x: x.type is not t_type, p_tokens))
