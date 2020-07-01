from __future__ import annotations

import functools
import typing as tp
import pylox.abstract_execs as ae
import pylox.lox_errors as le
import pylox.lox_ops as lo
import pylox.lox_utils as lu
import pylox.misc_utils as mu
import pylox.token_classes as tc
import pylox.token_utils as tu
from pylox import expr
from pylox.token_classes import TokenType as tt

error = functools.partial(le.error, error_type=le.ErrorReturns.PARSE_ERROR)


def primary(tokens: tc.TokenSeq) -> ae.Expr:
    err_message = "Expect expression"
    matched = None
    if not tokens:
        # Maybe add an error message here?
        return expr.ErrorExpr()
    if len(tokens) == 1:
        try:
            return expr.from_token(tokens[0])
        except ValueError:
            err_message = f'There is no literal "{tokens[0].lexeme}"'
    elif tokens[0].type is tt.SUPER:
        if tokens[1].type is not tt.DOT:
            error(tokens[1].line, f'Expect "." after "super".')
        elif tokens[2].type is not tt.IDENTIFIER:
            error(tokens[2].line, f'Expect "." after "super".')
        else:
            return expr.Super(tokens[0], tokens[2])
        return expr.ErrorExpr()
    else:
        matched = tu.matched_paren(tokens)
    if matched == "matched":
        return expr.Grouping(expression(tokens[1:-1]))
    error(tokens[0].line, err_message)
    return expr.ErrorExpr()


# TODO: Fix edge cases
def function_args(
    tokens: tp.Iterable[tc.Token], required_type: tp.Optional[tt] = None,
) -> tp.Iterator[tp.Optional[tc.Token]]:
    split_tokens = tu.specified_token_split(tokens, tt.COMMA)
    for i, argument in enumerate(split_tokens):
        if i >= 255:
            error(argument[0].line, "Cannot have more than 255 arguments.")
            break
        if mu.get(argument, 1) is not None:  # type: ignore
            error(argument[1].line, "Only a singular name is allowed")
        elif (
            required_type is None and argument.peek(tc.sentinel_token).type is tt.EMPTY
        ) and argument.peek(tc.sentinel_token).type is not required_type:
            next_t = argument.peek(tc.sentinel_token)
            error(
                next_t.line if next_t.type is not tt.EMPTY else "unknown",
                "Expect parameter name.",
            )
        elif argument:
            yield argument[0]
            continue
        yield None


CallIncrements: tp.Dict[tt, int] = {tt.DOT: 3, tt.RIGHT_PAREN: 2, tt.LEFT_PAREN: 1}


def call(tokens: tc.TokenSeq) -> ae.Expr:
    last_paren = next(tu.token_find_index(tokens, {tt.LEFT_PAREN, tt.DOT}), len(tokens))
    if last_paren == 0:
        return primary(tokens)
    if tokens[last_paren - 1].type is tt.SUPER:
        lox_function = primary(tokens[: last_paren + 2])
    else:
        lox_function = primary(tokens[:last_paren])
    for paren_index in tu.token_find_index(tokens, {tt.RIGHT_PAREN, tt.DOT}):
        if tokens[paren_index].type is tt.RIGHT_PAREN:
            args = tuple(
                function_args(
                    tokens[
                        last_paren
                        + CallIncrements[tokens[last_paren].type] : paren_index
                    ]
                )
            )
            if any(arg is None for arg in args):
                return expr.ErrorExpr()
            lox_function = expr.Call(
                lox_function,
                tokens[paren_index],
                [primary([tp.cast(tc.Token, x)]) for x in args],
            )
        elif tokens[paren_index - 1].type is not tt.SUPER:
            lox_function = expr.Get(lox_function, tokens[paren_index + 1])
        last_paren = paren_index
    return lox_function


def unary(tokens: tc.TokenSeq) -> ae.Expr:
    try:
        if tokens[0].type in lo.UNARY_FUNCTIONS:
            return expr.Unary(tokens[0], unary(tokens[1:]))
    except IndexError:
        return expr.ErrorExpr()
    other = next(tu.token_find_gen_ignore_first(tokens, lo.UNARY_FUNCTIONS), None)
    if other is None:
        return call(tokens)
    operator = tokens[other]
    if other == len(tokens) - 1:
        error(operator.line, f"{operator.lexeme} is not a postfix operator")
    else:
        error(operator.line, f"{operator.lexeme} is not a infix operator")
    return expr.ErrorExpr()


BinaryExprFunc = tp.Callable[[tc.TokenSeq], ae.Expr]


def binary_expr(
    types: tp.Container[tc.TokenType],
    next_func: BinaryExprFunc,
    expr_type: tp.Type[ae.BinaryExpr] = expr.Binary,
) -> BinaryExprFunc:
    def binary(tokens: tc.TokenSeq) -> ae.Expr:
        indexes = tu.token_find_gen_ignore_first(tokens, types)
        try:
            index, indexes = mu.peek_iter(indexes)
        except StopIteration:
            try:
                operator = tokens[0]
            except IndexError:
                return expr.ErrorExpr()
            if operator.type in types:
                error(operator.line, f"{operator} is not allowed as a prefix")
            return next_func(tokens)
        current_expr = next_func(tokens[:index])
        for first, second in mu.pairwise(indexes):
            current_expr = expr_type(
                current_expr, tokens[first], next_func(tokens[first + 1 : second])
            )
        # The MyPy can't detect this, but current_expr has to be a
        # expr.Binary because if it was empty it would of returned
        # already, so the above for loop runs at least once and sets
        # current_expr to a expr.Binary.
        right = current_expr.right  # type: ignore
        operator = current_expr.operator  # type: ignore
        if isinstance(right, expr.ErrorExpr):
            error(operator.line, f"{operator} is not allowed as a postfix")
        return current_expr

    return binary


def assignment(tokens: tc.TokenSeq) -> ae.Expr:
    equal_index = next(tu.token_find_index(tokens, {tt.EQUAL}), None)
    if equal_index is None or not lu.is_lox_identifier(tokens[:equal_index]):
        return logic_or(tokens)
    var = call(tokens[:equal_index])
    if not isinstance(var, (expr.Variable, expr.Get)):
        error(tokens[equal_index].line, "Invalid assignment target.")
        return expr.ErrorExpr()
    value = equality(tokens[equal_index + 1 :])
    if isinstance(var, expr.Get):
        return expr.Set(var, value)
    return expr.Assign(var.name, value)


multiplication = binary_expr({tt.SLASH, tt.STAR}, unary)
addition = binary_expr({tt.MINUS, tt.PLUS}, multiplication)
comparison = binary_expr(
    {tt.GREATER_EQUAL, tt.GREATER, tt.LESS_EQUAL, tt.LESS}, addition
)
equality = binary_expr({tt.BANG_EQUAL, tt.EQUAL_EQUAL}, comparison)
logic_and = binary_expr({tt.AND}, equality, expr.Logical)
logic_or = binary_expr({tt.OR}, logic_and, expr.Logical)
expression = assignment


def conditional(tokens: tc.TokenSeq) -> ae.Expr:
    """
    Pseudo expression for parsing if and while statements.
    Assumes the starting statement is included
    """
    if not tu.paren_check(tokens):
        return expr.ErrorExpr()
    return expression(tokens[2:-1])
