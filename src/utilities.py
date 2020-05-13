from __future__ import annotations
import classes as lc
import expr
import typing
import token_types as tt


def lox_true(value: lc.lox_literal) -> bool:
    if value is False or value is lc.nil:
        return False
    return True


def lox_type(value: lc.lox_literal) -> str:
    """ Returns the lox type of the literal. Considers ints a number lox type"""
    if value is lc.nil:
        return 'nil'
    elif isinstance(value, (float, int)):
        return 'number'
    elif isinstance(value, str):
        return 'string'
    elif isinstance(value, bool):
        return 'boolean'
    raise ValueError("Value is not lox literal")


def lox_str(value: lc.lox_literal) -> str:
    lox_rep = str(value)
    if lox_rep[-2:] == '.0':
        lox_rep = lox_rep[:-2]
    elif lox_rep == "True":
        lox_rep = "true"
    elif lox_rep == "False":
        lox_rep = "false"
    elif isinstance(value, str):
        lox_rep = f'"{lox_rep}"'
    return lox_rep


def token_string(tokens: typing.Iterable[lc.Token]) -> str:
    lexemes = ""
    for token in tokens:
        lexemes += token.lexeme
    return lexemes


def parenthesize_expr(name: str, *expressions: expr.Expr) -> str:
    text = f"({name}"
    for expression in expressions:
        text += f" {expression}"
    return text + ')'


class MatchedParenNT(typing.NamedTuple):
    """ NamedTuple matched_paren function returns """
    paren: typing.Literal["left", "right", "matched"]
    line: int


def matched_paren(tokens: typing.Sequence[lc.Token]) -> MatchedParenNT:
    paren_level = 0
    line = tokens[0].line
    for c, token in enumerate(tokens):
        if token.type in {tt.LEFT_PAREN, tt.RIGHT_PAREN}:
            line = token.line
        if token.type is tt.LEFT_PAREN:
            paren_level += 1
        elif token.type is tt.RIGHT_PAREN:
            paren_level -= 1
    if paren_level > 0:
        value = "left"
    elif paren_level < 0:
        value = "right"
    else:
        value = "matched"
    # noinspection PyTypeChecker
    return MatchedParenNT(value, line)


def split_tokens(tokens: typing.Iterable[lc.Token]
                 ) -> typing.List[typing.List[lc.Token]]:
    """ Splits the tokens on semicolons. Does not include the semicolon """
    tokens_list = []
    current_tokens = []
    for token in tokens:
        if token.type is tt.SEMICOLON:
            tokens_list.append(current_tokens)
            current_tokens = []
        else:
            current_tokens.append(token)
    return tokens_list


def type_in_tokens(tokens: typing.Iterable[lc.Token],
                   token_types: typing.Container[lc.TokenType]) -> bool:
    for token in tokens:
        if token.type in token_types:
            return True
    return False


class _TokenIndexNTBase(typing.NamedTuple):
    index: int
    token: lc.Token


class TokenIndexNT(_TokenIndexNTBase):
    def __getattr__(self, name):
        return getattr(self.token, name)


IndexToken = typing.Union[TokenIndexNT, lc.Token]


def it_enumerate(tokens: typing.Iterable[IndexToken]
                 ) -> typing.Generator[typing.Tuple[int, IndexToken], None, None]:
    for c, token in enumerate(tokens):
        if isinstance(token, TokenIndexNT):
            index = token.index
        else:
            index = c
        yield index, token


def non_parens(tokens: typing.Iterable[IndexToken]
               ) -> typing.Generator[TokenIndexNT, None, None]:
    paren_level = 0
    for c, token in it_enumerate(tokens):
        t_type = token.type
        if t_type is tt.RIGHT_PAREN:
            paren_level += 1
        elif t_type is tt.LEFT_PAREN:
            paren_level -= 1
        elif paren_level == 0:
            yield TokenIndexNT(c, token)


def strip_minuses(tokens: typing.Iterable[IndexToken]
                  ) -> typing.Generator[lc.Token, None, None]:
    seen_non_minus = False
    for c, token in it_enumerate(tokens):
        if token.token.type != tt.MINUS:
            seen_non_minus = True
        if seen_non_minus:
            yield TokenIndexNT(c, token)
