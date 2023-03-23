from typing import Any, Generator, Optional, Callable
from .ast_nodes import *
from .lexer import Token, TokenType


class Parser:
    def __init__(self, source_code: str, tokens: Generator[Token, None, None]):
        self.source_code = source_code
        self.tokens = tokens
        self.current_token: Optional[Token] = None
        self.next()

    def next(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None
        return self.current_token

    def parse(self):
        return self.function_declaration()

    def program(self):
        # Implement program rule
        pass

    def import_statement(self):
        # Implement import_statement rule
        pass

    def structure_declaration(self):
        # Implement structure_declaration rule
        pass

    def function_declaration(self) -> FunctionDeclaration:
        self.expect(TokenType.KEYWORD, 'fn')
        name = self.expect(TokenType.IDENTIFIER)
        [arguments, return_type, block] = self.function_after_identifier()
        return FunctionDeclaration(name.value, arguments, return_type, block)

    def function_after_identifier(self):
        self.expect(TokenType.SYMBOL, '(')
        self.skip_newlines()
        arguments = self.argument_list() if self.match(TokenType.IDENTIFIER) else []
        self.expect(TokenType.SYMBOL, ')')
        return_type = None
        if self.match(TokenType.SYMBOL, "->"):
            self.next()
            return_type = self.accessible_type_expression()
        return arguments, return_type, self.block()

    def block(self):
        self.expect(TokenType.SYMBOL, "{")
        self.skip_newlines()

        statements = []
        return_expression = None
        if self.has_next_statement():
            statements = self.statement_list()
        if self.match(TokenType.KEYWORD, "return"):
            self.next()
            return_expression = self.statement()
            self.skip_newlines()
        self.expect(TokenType.SYMBOL, "}")

        return Block(statements, return_expression)

    def has_next_statement(self):
        return not (self.match(TokenType.KEYWORD, "return") or self.match(TokenType.SYMBOL, "}"))

    def go_next_statement(self):
        if not self.match(TokenType.NEWLINE):
            return False
        self.skip_newlines()
        return self.has_next_statement()

    def statement_list(self):
        statements = [self.statement()]
        while self.go_next_statement():
            statements.append(self.statement())
        return statements

    def statement(self):
        return self.expression()

    def argument_list(self):
        arguments = [self.argument()]
        while self.match(TokenType.SYMBOL, ","):
            self.next()
            self.skip_newlines()
            if not self.match(TokenType.IDENTIFIER):
                break
            arguments.append(self.argument())
        return arguments

    def argument(self):
        identifier = Identifier(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.SYMBOL, ":")
        type_expression = self.accessible_type_expression()
        return Argument(identifier, type_expression)

    def accessible_type_expression(self) -> AccessibleTypeExpression:
        name = self.expect(TokenType.TYPE_EXPRESSION)
        child = None
        if self.match(TokenType.SYMBOL, "."):
            self.next()
            child = self.accessible_type_expression()
        return AccessibleTypeExpression(name.value, child)

    def export_statement(self):
        # Implement export_statement rule
        pass

    def type_expression(self):
        # Implement type_expression rule
        pass

    def expression(self):
        return self.or_expression()

    def or_expression(self):
        return self.binary_expression(self.and_expression, '||')

    def and_expression(self):
        return self.binary_expression(self.equality_expression, '&&')

    def equality_expression(self):
        return self.binary_expression(self.relational_expression, '==', '!=')

    def relational_expression(self):
        return self.binary_expression(self.range_expression, '<', '<=', '>', '>=')

    def range_expression(self):
        return self.binary_expression(self.additive_expression, '...', '..<')

    def additive_expression(self):
        return self.binary_expression(self.multiplicative_expression, '+', '-')

    def multiplicative_expression(self):
        return self.binary_expression(self.unary_expression, '*', '/', '%')

    def binary_expression(self, next_expression_fn: Callable[[], ASTNode], *ops: str):
        left = next_expression_fn()

        while self.current_token and self.current_token.type == TokenType.OPERATOR and self.current_token.value in ops:
            op = self.current_token.value
            self.next()
            self.skip_newlines()
            right = next_expression_fn()
            left = BinaryExpression(left, op, right)

        return left

    def unary_expression(self) -> ASTNode:
        if self.current_token and self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['!', '-']:
            op = self.current_token.value
            self.next()
            return UnaryExpression(op, self.primary_expression())
        else:
            return self.primary_expression()

    def primary_expression(self) -> ASTNode:
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.next()
            return IdentifierExpression(name)
        elif self.current_token.type in [TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL, TokenType.BOOLEAN_LITERAL]:
            literal_type = self.current_token.type
            if literal_type == TokenType.INTEGER_LITERAL:
                value = int(self.current_token.value)
            elif literal_type == TokenType.FLOAT_LITERAL:
                value = float(self.current_token.value)
            elif literal_type == TokenType.BOOLEAN_LITERAL:
                value = self.current_token.value == 'true'
            self.next()
            return LiteralExpression(value, literal_type)
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.next()

    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        if self.match(token_type, value):
            token = self.current_token
            self.next()
            return token
        else:
            error_line = self.source_code.split(
                '\n')[self.current_token.line - 1]
            raise SyntaxError(
                f"Expected {token_type} with value '{value}', but got {self.current_token.type} with value '{self.current_token.value}'\n"
                f"at {self.current_token.file_path}, line {self.current_token.line}, column {self.current_token.column}\n"
                f"{error_line}\n"
                f"{' ' * (self.current_token.column - 1)}^")

    def match(self, token_type: TokenType, value: Optional[str] = None):
        return self.current_token.type == token_type and (value is None or self.current_token.value == value)
