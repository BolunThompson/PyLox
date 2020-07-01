from __future__ import annotations

import typing as tp

import pylox.abstract_execs as ae
import pylox.error_dec as ed
import pylox.lox_errors as le
import pylox.stmt_parse as sp
import pylox.token_classes as tc


@ed.lox_error_handling(le.ErrorReturns.PARSE_ERROR)
def parse(
    tokens: tp.Sequence[tc.Token],
) -> tp.Union[tp.Tuple[ae.Stmt, ...], le.ErrorReturns]:
    """ Parses the tokens. Also could be named program() """
    statements = tuple(sp.from_tokens(tokens))
    if ae.has_error(statements):
        return le.ErrorReturns.PARSE_ERROR
    return statements
