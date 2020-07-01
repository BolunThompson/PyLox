from __future__ import annotations

import functools
import typing as tp
from collections import defaultdict

import pylox.error_dec as ed
import pylox.expr_parse as ep
import pylox.lox_class as lc
import pylox.lox_types as lt
import pylox.misc_utils as mu
import pylox.split_tokens as sp
import pylox.token_classes as tc
import pylox.token_utils as tu
from pylox import expr, stmt
from pylox.token_classes import TokenType as tt

if tp.TYPE_CHECKING:
    import pylox.abstract_execs as ae
    import pylox.functions as fn

    ProgramFunc = tp.Callable[[tp.Sequence[tc.Token]], ae.Stmt]
    MethodDefaultDict = tp.DefaultDict[lc.MethodType, tp.List[fn.LoxFunction]]

error = ep.error
stmt_print = functools.partial(ed.error_print, error_exec=stmt.ErrorStmt)


@stmt_print('Expect ";" after value')
def to_print(tokens: tp.Sequence[tc.Token]) -> stmt.PrintStmt:
    return stmt.PrintStmt(ep.expression(tokens[1:]))


@stmt_print('Expect ";" after expression')
def to_expr(tokens: tp.Sequence[tc.Token]) -> stmt.ExprStmt:
    return stmt.ExprStmt(ep.expression(tokens))


def to_var(tokens: tp.Sequence[tc.Token]) -> tp.Union[stmt.ErrorStmt, stmt.VarStmt]:
    relevant_tokens = tu.token_find_index(tokens, {tt.IDENTIFIER, tt.EQUAL})
    index = next(relevant_tokens, None)
    name = tokens[index] if index is not None else tc.sentinel_token
    if name.type is not tt.IDENTIFIER:
        error(name.line, "Expect variable name.")
        return stmt.ErrorStmt()
    equal_index = next(relevant_tokens, None)
    if equal_index is None and index != len(tokens) - 1:
        error(
            name.line, "Expect nothing between the variable name and the equals sign."
        )
        return stmt.ErrorStmt()
    initializer = (
        ep.expression(tokens[equal_index + 1 :]) if equal_index is not None else None
    )
    return stmt.VarStmt(name, initializer)


def to_brace(tokens: tc.TokenSeq,) -> stmt.BraceStmt:
    return stmt.BraceStmt(tuple(from_tokens(tokens[1:-1])))


def to_if(tokens: tc.TokenSeq) -> tp.Union[stmt.IfStmt, stmt.ErrorStmt]:
    paren = next(tu.token_find_index(tokens, {tt.RIGHT_PAREN}), len(tokens))
    condition = ep.conditional(tokens[: paren + 1])
    if condition.has_error():
        return stmt.ErrorStmt()
    else_index = next(tu.token_find_index(tokens, {tt.ELSE}), len(tokens))
    then_stmt = to_meta_dec(tokens[paren + 1 : else_index])
    else_stmt = to_meta_dec(tokens[else_index:]) if tokens[else_index:] else None
    return stmt.IfStmt(condition, then_stmt, else_stmt)


def to_while(tokens: tc.TokenSeq) -> tp.Union[stmt.WhileStmt, stmt.ErrorStmt]:
    right_paren = next(tu.token_find_index(tokens, {tt.RIGHT_PAREN}), len(tokens))
    condition = ep.conditional(tokens[: right_paren + 1])
    if condition.has_error():
        return stmt.ErrorStmt()
    body = to_meta_dec(tokens[right_paren + 1 :])
    return stmt.WhileStmt(condition, body)


FirstClauseType = tp.Union[stmt.ExprStmt, stmt.NullStmt, stmt.VarStmt, stmt.ErrorStmt]


def first_for_clause(
    clause: tp.Optional[tc.TokenSeq], error_line: int
) -> FirstClauseType:
    if clause is None:
        error(error_line, "Need for loop clauses.")
        return stmt.ErrorStmt()
    if not clause:
        return stmt.NullStmt()
    first_type = clause[0].type
    if first_type is tt.VAR:
        return to_var(clause)
    if first_type not in PROGRAM_FUNCS:
        return to_expr(clause)
    error(clause[-1].line, "Invalid statement in for loop initializer")
    return stmt.ErrorStmt()


def second_for_clause(
    clause: tp.Optional[tc.TokenSeq], error_line: int
) -> tp.Optional[ae.Expr]:
    if clause is None:
        error(error_line, "Need second for loop clause.")
        return expr.ErrorExpr()
    if not clause:
        return None
    return ep.expression(clause)


def third_for_clause(clause: tp.Optional[tc.TokenSeq]) -> tp.Optional[ae.Expr]:
    return ep.expression(clause) if clause else None


class ForClausesNT(tp.NamedTuple):
    initializer: FirstClauseType
    condition: tp.Optional[ae.Expr]
    increment: tp.Optional[ae.Expr]

    def has_error(self) -> bool:
        return any(clause is not None and clause.has_error() for clause in self)


error_for_clauses = ForClausesNT(stmt.ErrorStmt(), expr.ErrorExpr(), expr.ErrorExpr())


def for_clauses(clauses: tc.TokenSeq) -> ForClausesNT:
    """
    Helper function to parse the clauses of a for loop.
    Assumes the parentheses are for token is included.
    """
    if not tu.paren_check(clauses):
        return error_for_clauses
    split_tokens = (
        tuple(x) for x in tu.specified_token_split(clauses[2:-1], tt.SEMICOLON)
    )
    first_clause = first_for_clause(next(split_tokens, None), clauses[-1].line)
    second_clause = second_for_clause(next(split_tokens, None), clauses[-1].line)
    third_clause = third_for_clause(next(split_tokens, None))
    return ForClausesNT(first_clause, second_clause, third_clause)


def to_for(tokens: tp.Iterable[tc.Token]) -> ae.Stmt:
    iter_tokens = iter(tokens)
    clauses = for_clauses(tuple(sp.parens(iter_tokens)))
    if clauses.has_error():
        return stmt.ErrorStmt()
    body = to_meta_dec(tuple(iter_tokens))
    if clauses.increment is not None:
        # Not a function, but function_scope is true to prevent the
        # creation of unnecessary scopes.
        body = stmt.BraceStmt(
            (body, stmt.ExprStmt(clauses.increment)), function_scope=True
        )
    body = stmt.WhileStmt(clauses.condition or expr.Literal(True), body)
    body = stmt.BraceStmt((clauses.initializer, body))
    return body


def to_fun(
    tokens: tc.TokenSeq, kind: str,
) -> tp.Union[stmt.ErrorStmt, stmt.FunctionStmt]:
    name = tokens[1]
    if name.type is not tt.IDENTIFIER:
        error(name.line, f"Expect {kind} name")
        return stmt.ErrorStmt()
    i_tokens = iter(tokens[1:])
    parens = tuple(sp.parens(i_tokens))
    if not tu.paren_check(parens):
        return stmt.ErrorStmt()
    arguments = tuple(ep.function_args(parens[2:-1], tt.IDENTIFIER))
    if any(arg is None for arg in arguments):
        return stmt.ErrorStmt()
    body = to_meta_dec(tuple(i_tokens))
    if not isinstance(body, stmt.BraceStmt):
        error(name.line, "Expect braced statement after function")
        return stmt.ErrorStmt()
    body.function_scope = True
    return stmt.FunctionStmt.from_params(arguments, body, name)  # type: ignore


def to_return(tokens: tc.TokenSeq) -> stmt.ReturnStmt:
    nil_expr = [tc.Token(tt.NIL, "nil", lt.nil, tokens[0].line)]
    value = ep.expression(tokens[1:] or nil_expr)
    return stmt.ReturnStmt(tokens[0], value)


def to_methods(tokens: tc.TokenSeq) -> tp.Iterator[lc.MethodNT]:
    """ Pseudo statement parsing function to parse class methods. """
    for method in sp.a_match_braces(tokens):
        if method.peek().type is tt.CLASS:
            yield lc.MethodNT(
                to_fun(tuple(method), "static method"), lc.MethodType.STATIC
            )
        elif method[1].type is not tt.LEFT_PAREN:
            getter_tokens = (
                tc.sentinel_token,
                next(method),
                tc.Token(tt.LEFT_PAREN, "(", None, method[-1].line),
                tc.Token(tt.RIGHT_PAREN, ")", None, method[-1].line),
                *method,
            )
            yield lc.MethodNT(
                to_fun(getter_tokens, "getter method",), lc.MethodType.PROPERTY,
            )
        else:
            yield lc.MethodNT(
                to_fun((tc.sentinel_token, *method), "method"), lc.MethodType.BOUND
            )


def filter_methods(tokens: tp.Iterable[lc.MethodNT]) -> tp.Optional[MethodDefaultDict]:
    methods: MethodDefaultDict = defaultdict(list)
    for token_nt in tokens:
        if token_nt.function.has_error():
            return None
        methods[token_nt.type].append(
            tp.cast(stmt.FunctionStmt, token_nt.function).function
        )
    return methods


def to_class(tokens: tc.TokenSeq) -> tp.Union[stmt.ClassStmt, stmt.ErrorStmt]:
    if mu.get(tokens, 1, tc.sentinel_token).type is not tt.IDENTIFIER:
        error(tokens[0].line, "Expect class name")
        return stmt.ErrorStmt()
    if mu.get(tokens, 2, tc.sentinel_token).type is tt.LESS:
        token_s_class = mu.get(tokens, 3, tc.sentinel_token)
        if token_s_class.type is not tt.IDENTIFIER:
            error(tokens[2].line, "Expect superclass name")
            stmt.ErrorStmt()
        super_class: tp.Optional[expr.Variable] = expr.Variable(token_s_class)
        first_brace = 4
    else:
        super_class = None
        first_brace = 2
    if mu.get(tokens, first_brace, tc.sentinel_token).type is not tt.LEFT_BRACE:
        error(tokens[2].line, 'Expect "{" before class body')
    # This should be the right brace of the last method declaration or
    # the left_brace starting the class if the class is empty.
    elif (
        tokens[-1].type is not tt.RIGHT_BRACE
        and mu.get(tokens, first_brace, tc.sentinel_token) is not tokens[-1]
    ):
        error(tokens[-1].line, 'Expect "}" after class body')
    else:
        methods = filter_methods(to_methods(tokens[first_brace + 1 : -1]))
        if methods is not None:
            return stmt.ClassStmt.from_params(
                tokens[1],
                super_class,
                methods[lc.MethodType.BOUND],
                methods[lc.MethodType.STATIC],
                methods[lc.MethodType.PROPERTY],
            )
    return stmt.ErrorStmt()


PROGRAM_FUNCS: tp.DefaultDict[tc.TokenType, ProgramFunc] = defaultdict(
    lambda: to_expr,
    {
        tt.VAR: to_var,
        tt.LEFT_BRACE: to_brace,
        tt.IF: to_if,
        tt.PRINT: to_print,
        tt.WHILE: to_while,
        tt.FOR: to_for,
        tt.BREAK: lambda x: stmt.BreakStmt(x[0]),
        tt.FUN: functools.partial(to_fun, kind="function"),
        tt.RETURN: to_return,
        tt.CLASS: to_class,
    },
)


# TODO: Rename
def to_meta_dec(tokens: tp.Sequence[tc.Token]) -> ae.Stmt:
    if tokens:
        return PROGRAM_FUNCS[tokens[0].type](tokens)
    return stmt.NullStmt()


# TODO: Rename?
def from_tokens(tokens: tp.Iterable[tc.Token]) -> tp.Iterator[ae.Stmt]:
    """ Returns an iterator of declarations from a list of tokens."""
    # if not tu.check_matching(tokens):
    #     yield stmt.ErrorStmt()
    #     yield from from_tokens(tuple(tu.synchronize(tokens)))
    #     return
    for stmt_tokens in sp.split_tokens(tokens):
        result = to_meta_dec(tuple(stmt_tokens))
        if result.has_error():
            yield stmt.ErrorStmt()
            yield from from_tokens(tu.synchronize(stmt_tokens))
        else:
            yield result
