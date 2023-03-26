import re
from enum import Enum, auto
from typing import NamedTuple, Any


class TokenType(Enum):
    KEYWORD = auto()
    TYPE_EXPRESSION = auto()
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    BOOLEAN_LITERAL = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    COMMENT = auto()
    OPERATOR = auto()
    SYMBOL = auto()


class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int, file_path: str):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.file_path = file_path

    def __str__(self):
        return f"{self.type.name}({self.value}) at {self.file_path}, line {self.line}, column {self.column}"


token_types = [
    (TokenType.KEYWORD.name,
     r'\b(?:import|as|struct|pub|const|var|fn|export|return|if|else|throws|async)\b'),
    (TokenType.TYPE_EXPRESSION.name, r'[A-Z][a-zA-Z0-9]*'),
    (TokenType.IDENTIFIER.name, r'[a-z][a-zA-Z0-9]*'),
    (TokenType.FLOAT_LITERAL.name, r'\d+\.\d+'),
    (TokenType.INTEGER_LITERAL.name, r'\d+'),
    (TokenType.STRING_LITERAL.name, r'"(?:[^"\\]|\\.)*"'),
    (TokenType.BOOLEAN_LITERAL.name, r'\b(?:true|false)\b'),
    (TokenType.WHITESPACE.name, r'[ \t]+'),
    (TokenType.NEWLINE.name, r'\n'),
    (TokenType.COMMENT.name, r'(?:\/\/[^\n]*|\/\*(?:.|\n)*?\*\/)'),
    (TokenType.SYMBOL.name, r'(?:->|/>|</)|[{}()\[\],.:;<>]'),
    (TokenType.OPERATOR.name,
     r'[+\-*/%^!=<>&|]|(?:\.\.<|==|!=|<=|>=|&&|\|\||\.\.\.)'),
]

pattern = '|'.join('(?P<%s>%s)' % pair for pair in token_types)
token_regex = re.compile(pattern)


def tokenize(source_code: str, file_path: str):
    line_num = 1
    col_num = 1

    for m in re.finditer(token_regex, source_code):
        token_type = TokenType[m.lastgroup]
        token_value = m.group(token_type.name)

        if token_type == TokenType.WHITESPACE or token_type == TokenType.COMMENT:
            pass
        else:
            yield Token(token_type, token_value, line_num, col_num, file_path)

        col_num += len(token_value)
        line_num += token_value.count('\n')
        col_num = 1 if '\n' in token_value else col_num
