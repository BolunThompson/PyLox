import sys
import typing

import scanner
import lparser as parser
import LoxErrors as le
import utilities as lu


def run(source: str) -> typing.Union[str, le.ErrorReturns]:
    tokens = scanner.scan(source)
    if tokens is le.ErrorReturns.SCAN_ERROR:
        return le.ErrorReturns.SCAN_ERROR
    ast = parser.expr_parse(tokens)
    if ast is le.ErrorReturns.PARSE_ERROR:
        return le.ErrorReturns.PARSE_ERROR
    result = ast.interpret()
    if result is le.ErrorReturns.RUNTIME_ERROR:
        return le.ErrorReturns.RUNTIME_ERROR
    return lu.lox_str(result)


def repl() -> None:
    print("Lox REPL")
    while True:
        try:
            result = run(input("$>> "))
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
        else:
            if not isinstance(result, le.ErrorReturns):
                print(result)
        le.line_increment += 1
    print()


def runfile(path: str) -> typing.Union[str, le.ErrorReturns]:
    """ Same as run() except a file path is provided """
    with open(path) as file:
        program = file.read()
    return run(program)


def main(file: typing.Optional[str] = None) -> int:
    if file is not None:
        result = runfile(file)
        if isinstance(result, le.ErrorReturns):
            return result.value
    else:
        repl()
    return 0


def cli() -> typing.NoReturn:
    code = 0
    if len(sys.argv) > 2:
        print("Usage: pylox [file_path]")
        code = 64
    elif len(sys.argv) == 2:
        code = main(sys.argv[1])
    else:
        main()
    sys.exit(code)


if __name__ == '__main__':
    cli()
