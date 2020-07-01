from __future__ import annotations

import dataclasses
import typing as tp

import pylox.lox_errors as le
import pylox.lox_types as lt


class ResultNT(tp.NamedTuple):
    result: lt.StmtLiteral
    status: le.ErrorReturns = le.ErrorReturns.SUCCESS


@dataclasses.dataclass
class ReturnList(tp.List[ResultNT]):
    """ List with a lox_errors.Returns status """

    status: le.ErrorReturns = le.ErrorReturns.SUCCESS
