from .lexer import tokenize
from .parser import Parser


def createAst(source_code: str, file_path: str):
    tokens = tokenize(source_code, file_path)
    parser = Parser(source_code, tokens)
    return parser.parse()
