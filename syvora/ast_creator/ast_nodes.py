from typing import List, Optional
from .lexer import TokenType


class ASTNode:
    pass


class Module(ASTNode):
    def __init__(self, functions: List['FunctionDeclaration']):
        self.functions = functions


class FunctionDeclaration(ASTNode):
    def __init__(self, name: str, arguments: list['Argument'], return_type: Optional['AccessibleTypeExpression'], body: 'Block'):
        self.name = name
        self.arguments = arguments
        self.return_type = return_type
        self.body = body


class Argument(ASTNode):
    def __init__(self, identifier: 'Identifier', type: 'AccessibleTypeExpression'):
        self.identifier = identifier
        self.type = type


class IfExpression(ASTNode):
    def __init__(self, condition, true_block, false_block):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block


class FunctionCallExpression(ASTNode):
    def __init__(self, function_name: str, arguments: dict[str, ASTNode], children: Optional[list[ASTNode]] = None):
        self.function_name = function_name
        self.arguments = arguments
        self.children = children


class BinaryExpression(ASTNode):
    def __init__(self, left: ASTNode, operator, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})"


class UnaryExpression(ASTNode):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def __repr__(self):
        return f"({self.operator}{self.expression})"


class Block(ASTNode):
    def __init__(self, statements: List[ASTNode], return_expression: Optional[ASTNode]):
        self.statements = statements
        self.return_expression = return_expression

    def __repr__(self):
        return f"({self.statements}{self.return_expression})"


class IdentifierExpression(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"({self.name})"


class LiteralExpression(ASTNode):
    def __init__(self, value: int | float | bool, literal_type: TokenType):
        self.value = value
        self.literal_type = literal_type

    def __repr__(self):
        return f"{self.literal_type}({self.value})"


class AccessibleTypeExpression(ASTNode):
    def __init__(self, name: str, child: Optional['AccessibleTypeExpression']):
        self.name = name
        self.child = child


class TypeExpression(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"TypeExpression({self.name!r})"


class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Identifier({self.name!r})"
