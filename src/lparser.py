from __future__ import annotations
import typing
import classes as lc
import token_types as tt
import LoxErrors as le
import expr
import utilities as ut
import stmt


class TokenFindNT(typing.NamedTuple):
    index: typing.Optional[int]
    token: typing.Optional[lc.Token]


def token_find_last(token_seq: typing.Iterable[lc.Token],
                    token_types: typing.Container[tt.TokenType]
                    ) -> TokenFindNT:
    """
    Finds the index of the occurrences of the specified token_type
    or container of token_types in an sequence of tokens.
    Returns a tuple in the form (index, token_type_found) with
    token_type_found being the token type found.
    Returns None if the type isn't in token_seq
    """
    index = None
    final_token = None
    for c, token in ut.non_parens(ut.strip_minuses(token_seq)):
        if token.type in token_types:
            index = c
            final_token = token
    return TokenFindNT(index, final_token)


def primary(tokens: typing.Sequence[lc.Token]) -> expr.Expr:
    err_message = "Expect expression"
    line = tokens[0].line
    try:
        if len(tokens) == 1:
            err_message = "Invalid literal"
            return expr.Literal.from_token(tokens[0])
        matched = ut.matched_paren(tokens)
        if matched.paren == "left":
            err_message = "Unmatched '('"
        elif matched.paren == "right":
            err_message = "Unmatched ')'"
        elif matched.paren == "matched":
            return expr.Grouping(expression(tokens[1:-1]))
    except Exception:
        pass
    le.error(line, err_message)
    return expr.ErrorExpr()


def unary(tokens: typing.Sequence[lc.Token]) -> expr.Expr:
    matched_tt = {tt.BANG, tt.MINUS}
    try:
        if tokens[0].type in matched_tt:
            return expr.Unary(tokens[0], unary(tokens[1:]))
    except IndexError:
        return expr.ErrorExpr()
    other_bang = token_find_last(tokens, {tt.BANG}).index
    if other_bang == len(tokens) - 1:
        le.error(tokens[other_bang].line, "! is not a postfix operator")
    elif other_bang is not None:
        le.error(tokens[other_bang].line, "! is not a infix operator")
    return primary(tokens)


binary_expr_sig = typing.Callable[[typing.Sequence[lc.Token]], expr.Expr]


def binary_expr(types: typing.Container[tt.TokenType],
                next_func: binary_expr_sig) -> binary_expr_sig:
    def binary(tokens: typing.Iterable[lc.Token]) -> expr.Expr:
        tokens = list(tokens)
        if not tokens:
            return expr.ErrorExpr()
        # Cheat to improve error messages and performance
        elif len(tokens) == 1:
            return primary(tokens)
        index, op = token_find_last(tokens, types)
        if index is None:
            return next_func(tokens)
        line = tokens[index].line
        left = binary(tokens[:index])
        right = next_func(tokens[index+1:])
        if isinstance(left, expr.ErrorExpr):
            le.error(line, f"{op} is not allowed as a prefix")
        elif isinstance(right, expr.ErrorExpr):
            le.error(line, f"{op} is not allowed as a postfix")
        return expr.Binary(left, op, right)
    return binary


multiplication = binary_expr({tt.SLASH, tt.STAR}, unary)
addition = binary_expr({tt.MINUS, tt.PLUS}, multiplication)
comparison = binary_expr({tt.GREATER_EQUAL, tt.GREATER, tt.LESS_EQUAL, tt.LESS}, addition)
equality = binary_expr({tt.BANG_EQUAL, tt.EQUAL_EQUAL}, comparison)
expression = equality


def expr_parse(tokens: typing.Sequence[lc.Token]
               ) -> typing.Union[expr.Expr, typing.Literal[le.ErrorReturns.PARSE_ERROR]]:
    """ Parses the expressions."""
    # TODO: Add panic mode going to the next statement
    parsed_expr = expression(tokens)
    if not parsed_expr.has_error():
        return parsed_expr
    return le.ErrorReturns.PARSE_ERROR


def parse(tokens: typing.Sequence[lc.Token]
          ) -> typing.Union[typing.List[stmt.Stmt],
                            typing.Literal[le.ErrorReturns.PARSE_ERROR]]:
    """ Parses the tokens. Also could be named program() """
    statements = stmt.from_tokens(tokens)
    if statements is None:
        return le.ErrorReturns.PARSE_ERROR
    for statement in statements:
        if statement.has_error():
            return le.ErrorReturns.PARSE_ERROR
    return statements
