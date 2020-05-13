import typing
import token_types as tt
import classes as lc
import LoxErrors as le


def to_token_type(string: str, line: int,
                  ) -> typing.Optional[tt.TokenType]:
    token = None
    if string == '(':
        token = tt.LEFT_PAREN
    elif string == ')':
        token = tt.RIGHT_PAREN
    elif string == '{':
        token = tt.LEFT_BRACE
    elif string == '}':
        token = tt.RIGHT_BRACE
    elif string == ',':
        token = tt.COMMA
    elif string == '.':
        token = tt.DOT
    elif string == '-':
        token = tt.MINUS
    elif string == '+':
        token = tt.PLUS
    elif string == ';':
        token = tt.SEMICOLON
    elif string == '*':
        token = tt.STAR
    elif string == '!':
        token = tt.BANG
    elif string == '=':
        token = tt.EQUAL
    elif string == '<':
        token = tt.LESS
    elif string == '>':
        token = tt.GREATER
    elif string == '!=':
        token = tt.BANG_EQUAL
    elif string == '==':
        token = tt.EQUAL_EQUAL
    elif string == '<=':
        token = tt.LESS_EQUAL
    elif string == '>=':
        token = tt.GREATER_EQUAL
    elif string == '/':
        token = tt.SLASH
    elif string.replace('.', '', 1).replace('e+', '', 1).isdigit():
        token = tt.NUMBER
    elif string[0] == '"':
        token = tt.STRING
    elif string.isalpha() or string[0] == '_':
        token = tt.RESERVED_WORDS.get(string, tt.IDENTIFIER)
    # These are white space or comments that don't have a token
    elif string in {' ', '\r', '\t', '//', '', '\n', '/*', '*/'}:
        token = tt.EMPTY
    else:
        le.error(line, f"Unexpected Character {string}")
    return token


# TODO: Refactor
def scan(source: str) -> typing.Union[typing.List[lc.Token],
                                      typing.Literal[le.ErrorReturns.SCAN_ERROR]]:
    current = 0
    line = 1
    tokens: typing.List[lc.Token] = []
    errored = False
    while current < len(source):
        literal = None
        char = source[current]
        if char in {'!', '=', '<', '>'}:
            try:
                if source[current + 1] == '=':
                    current += 1
                    char += '='
            except IndexError:
                pass
        elif source[current: current+2] == '//':
            char = '//'
            try:
                current = source.index('\n', current)
            except ValueError:
                break
        elif source[current: current+2] == '/*':
            char = '/*'
            start_comment = current
            try:
                current = source.index('*/', start_comment) + 1
            except ValueError:
                break
            line += source.count('\n', start_comment, current)
        elif char == '\n':
            line += 1
        elif char == '"':
            text = ''
            current += 1
            try:
                while source[current] != '"':
                    text += source[current]
                    current += 1
            except IndexError:
                le.error(line, "Unterminated string literal")
                errored = True
                break
            literal = text
            char = f'"{text}"'
        if char.isdigit():
            digit_string = ""
            try:
                while (source[current].isdigit() or source[current] == '.'
                       or (source[current] == 'e' and source[current+1] == '+')
                       or (source[current] == '+' and source[current-1] == 'e')):
                    digit_string += source[current]
                    current += 1
            except IndexError:
                pass
            char = digit_string
            literal = float(digit_string)
        elif char.isalpha() or char[0] == '_':
            word = ""
            try:
                while source[current].isalnum() or source[current] == '_':
                    word += source[current]
                    current += 1
            except IndexError:
                pass
            p_reserved_word = tt.RESERVED_WORDS.get(word)
            char = word
            if p_reserved_word == 'true':
                literal = True
            elif p_reserved_word == 'false':
                literal = False
            elif p_reserved_word == 'nil':
                literal = lc.nil
        else:
            current += 1

        token_type = to_token_type(char, line)
        if token_type is None:
            errored = True
        elif token_type != tt.EMPTY:
            tokens.append(lc.Token(token_type, char, literal, line))

    return le.ErrorReturns.SCAN_ERROR if errored else tokens
