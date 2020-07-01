#!/usr/bin/env python3
from __future__ import annotations

import sys
import typing as tp

import pylox.error_dec as ed
import pylox.lox_errors as le
from pylox import interpreter, lparser, resolver, results, scanner


@ed.lox_keyboard_interrupt(le.ErrorReturns.RUNTIME_ERROR, 1)
def run(source: str) -> results.ReturnList:
    return interpreter.interpret(resolver.resolve(lparser.parse(scanner.scan(source))))


def repl() -> None:
    # TODO: Add ability to evaluate and then print expressions
    print("Lox REPL")
    # readline provides history and arrow key support in input().
    # It only needs to be imported
    # noinspection PyUnresolvedReferences
    import readline

    while True:
        try:
            text = input("$>> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
        else:
            run(text)
        le.line_inc += 1
    print()


def runfile(path: str) -> results.ReturnList:
    """ Same as run() except a file path is provided """
    try:
        with open(path) as file:
            program = file.read()
    except FileNotFoundError:
        print("File not found")
        return results.ReturnList(status=le.ErrorReturns.FILE_ERROR)
    return run(program)


def main(args: tp.Sequence[str]) -> int:
    if len(args) > 2:
        print("Usage: pylox [file_path]")
        return 64
    if len(args) == 2:
        return runfile(args[1]).status.value.code
    repl()
    return 0


def cli() -> tp.NoReturn:
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    cli()
