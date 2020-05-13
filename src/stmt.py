import dataclasses
import typing

import abstract_execs as ae
import lparser as lp
import token_types as tt
import classes as lc
import utilities as ut
import LoxErrors as le


class Stmt(ae.AbstractExec):
    def __str__(self):
        return f"{self.__class__.__name__} {[str(expr) for expr in self.exprs]}"


class ExprStmt(ae.ExprExecMixin, Stmt):
    pass


class PrintStmt(ae.ExprExecMixin, Stmt):
    pass


class ErrorStmt(ae.ErrorExecMixin, Stmt):
    pass


def from_individual_token(stmt_tokens: typing.Sequence[lc.Token]
                          ) -> typing.Optional[Stmt]:
    token = stmt_tokens[0]
    if token.type is tt.PRINT:
        remaining_tokens = stmt_tokens[1:]
        message = "Expect ';' after value"
        statement = PrintStmt
    else:
        remaining_tokens = stmt_tokens
        message = "Expect ';' after expression"
        statement = ExprStmt
    error = ut.type_in_tokens(remaining_tokens, tt.STMTS)
    if not error:
        parsed_expr = lp.expression(remaining_tokens)
        error = parsed_expr.has_error()
    if error:
        le.error(message=message)
        parsed_stmt = None
    else:
        # noinspection PyUnboundLocalVariable,PyArgumentList
        parsed_stmt = statement(parsed_expr)
    return parsed_stmt


def from_tokens(tokens: typing.Sequence[lc.Token]
                ) -> typing.Optional[typing.List[Stmt]]:
    """" Returns a list of statements from a list of tokens."""
    split_tokens = ut.split_tokens(tokens)
    statements = []
    for tokens in split_tokens:
        if ut.type_in_tokens(tokens, {tt.EOF}):
            break
        stmt = from_individual_token(tokens)
        if stmt is not None:
            statements.append(stmt)
        else:
            return
    return statements
