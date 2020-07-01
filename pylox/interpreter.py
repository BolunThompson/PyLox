from __future__ import annotations

import typing as tp

import pylox.error_dec as ed
import pylox.lox_errors as le
from pylox import results

if tp.TYPE_CHECKING:
    import pylox.abstract_execs as ae


@ed.lox_error_handling(le.ErrorReturns.RUNTIME_ERROR)
def interpret(ast: tp.Iterable[ae.AbstractExec]) -> results.ReturnList:
    results_list = results.ReturnList()
    for node in ast:
        result = node.interpret()
        if result.status.error():
            results_list.status = result.status
            return results_list
        results_list.append(result)
    return results_list
